"""PTY-backed interactive terminal exposed over a WebSocket.

Gives the user a real shell — for pdb, python, poking at files — rooted in the
problem directory. This is a single-user local tool: the shell runs with the
user's own privileges, exactly as if they opened a terminal themselves.

Wire protocol:
  client -> server : JSON text frames
      {"type": "input",  "data": "<keystrokes>"}
      {"type": "resize", "cols": <int>, "rows": <int>}
  server -> client : raw binary frames (PTY output bytes)
"""
from __future__ import annotations

import asyncio
import fcntl
import json
import os
import pty
import signal
import struct
import termios
from pathlib import Path

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

REPO_ROOT = Path(__file__).resolve().parent.parent
READ_CHUNK = 65536


def _child_env() -> dict:
    """Environment for the shell: real TERM, project venv first on PATH so
    `python`/`pdb` resolve to the same interpreter the test runner uses."""
    env = dict(os.environ)
    env["TERM"] = "xterm-256color"
    venv_bin = REPO_ROOT / ".venv" / "bin"
    if venv_bin.is_dir():
        env["PATH"] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
    return env


def _set_winsize(fd: int, rows: int, cols: int) -> None:
    if rows > 0 and cols > 0:
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


def _spawn_shell(cwd: Path) -> tuple[int, int]:
    """Fork an interactive shell on a fresh PTY. Returns (pid, master_fd)."""
    env = _child_env()
    shell = env.get("SHELL") or "/bin/bash"
    pid, master_fd = pty.fork()
    if pid == 0:  # child — replace ourselves with the shell
        try:
            os.chdir(cwd)
        except OSError:
            pass
        try:
            os.execvpe(shell, [shell], env)
        except OSError:
            os._exit(127)
    return pid, master_fd


async def _reap(pid: int) -> None:
    """Hang up, then kill, then wait — so no zombie is left behind."""
    try:
        os.kill(pid, signal.SIGHUP)
    except ProcessLookupError:
        return
    await asyncio.sleep(0.1)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        await asyncio.get_running_loop().run_in_executor(None, os.waitpid, pid, 0)
    except (ChildProcessError, OSError):
        pass


async def terminal_session(websocket: WebSocket, cwd: Path) -> None:
    await websocket.accept()
    pid, fd = _spawn_shell(cwd)
    os.set_blocking(fd, False)

    loop = asyncio.get_running_loop()
    out_queue: asyncio.Queue[bytes] = asyncio.Queue()
    closed = asyncio.Event()

    def on_readable() -> None:
        try:
            data = os.read(fd, READ_CHUNK)
        except OSError:
            data = b""  # PTY closed — the shell exited
        if data:
            out_queue.put_nowait(data)
        else:
            closed.set()

    loop.add_reader(fd, on_readable)

    async def pump_output() -> None:
        try:
            while True:
                await websocket.send_bytes(await out_queue.get())
        except (WebSocketDisconnect, RuntimeError, asyncio.CancelledError):
            pass
        finally:
            closed.set()

    async def pump_input() -> None:
        try:
            while True:
                payload = json.loads(await websocket.receive_text())
                kind = payload.get("type")
                if kind == "input":
                    os.write(fd, payload.get("data", "").encode("utf-8", "ignore"))
                elif kind == "resize":
                    _set_winsize(fd, int(payload.get("rows", 24)),
                                 int(payload.get("cols", 80)))
        except (WebSocketDisconnect, RuntimeError, OSError,
                json.JSONDecodeError, TypeError, asyncio.CancelledError):
            pass
        finally:
            closed.set()

    out_task = asyncio.create_task(pump_output())
    in_task = asyncio.create_task(pump_input())
    try:
        await closed.wait()
    finally:
        loop.remove_reader(fd)
        for task in (out_task, in_task):
            task.cancel()
        await asyncio.gather(out_task, in_task, return_exceptions=True)
        await _reap(pid)
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            await websocket.close()
        except (RuntimeError, OSError):
            pass
