"""The MockSignal copilot — a Mio-style pair-programmer.

MockSignal is a local-only tool (the terminal pane is a real PTY on your
machine), so instead of requiring an Anthropic API key the copilot shells out
to the locally-installed `claude` CLI — it reuses whatever login Claude Code
already has. The frontend posts the running chat plus a snapshot of what the
solver is looking at (problem, active level, current solution.py); we hand that
to `claude -p` and stream its reply back as Server-Sent Events.
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import tempfile
from typing import AsyncIterator, List, Optional

from pydantic import BaseModel

from . import problems

# Resolve the CLI once. Override with MOCKSIGNAL_CLAUDE_BIN if it isn't on PATH
# (e.g. a GUI-launched server with a minimal PATH).
CLAUDE_BIN = os.environ.get("MOCKSIGNAL_CLAUDE_BIN") or shutil.which("claude")

# Model alias passed to `claude --model`. "opus" is the most capable; override
# with MOCKSIGNAL_COPILOT_MODEL (e.g. "sonnet") for faster replies.
MODEL = os.environ.get("MOCKSIGNAL_COPILOT_MODEL", "opus")

# Tools we never want the copilot to reach for — it's a chat assistant, not an
# agent loose in the repo. (It also runs in a throwaway temp dir.)
DISALLOWED_TOOLS = ["Bash", "Edit", "Write", "MultiEdit", "NotebookEdit", "Task"]

OVERALL_TIMEOUT_SECONDS = 240  # generous — local CLI replies can be slow
MAX_HISTORY = 40               # cap how much chat we replay
MAX_FILE_CHARS = 12000         # per open-file content cap
MAX_TERMINAL_CHARS = 6000      # tail of the terminal transcript to include


class CopilotMessage(BaseModel):
    role: str            # "user" | "assistant"
    content: str


class OpenFile(BaseModel):
    name: str
    content: str = ""


class CopilotContext(BaseModel):
    problemName: Optional[str] = None
    problemTitle: Optional[str] = None
    description: Optional[str] = None
    activeLevel: Optional[int] = None
    levelMarkdown: Optional[str] = None
    code: Optional[str] = None                       # legacy fallback (solution.py)
    openFiles: Optional[List[OpenFile]] = None       # editor tabs + their contents
    terminalHistory: Optional[str] = None            # recent terminal transcript
    lastResults: Optional[str] = None


class CopilotBody(BaseModel):
    messages: List[CopilotMessage]
    context: Optional[CopilotContext] = None


SYSTEM_BASE = """\
You are Mio, the in-app coding copilot for MockSignal — a local practice \
environment styled after CodeSignal's Industry Coding Framework (ICF) \
assessment. The user is practicing timed, multi-level Python implementation \
problems and you are pair-programming alongside them in the IDE.

How to help:
- Be a genuine pair programmer: explain the problem, sketch approaches, reason \
about data structures and complexity, debug failing tests, and review the \
user's code.
- Match the user's intent. If they ask for a hint, give a nudge and stop — \
don't dump the whole solution. If they explicitly ask for the full \
implementation, write it.
- This is the user's own practice tool, not a live proctored exam, so you may \
be fully helpful. Still, default to building their understanding rather than \
just handing over answers.
- Be concise and direct. Use Markdown. Use fenced ```python blocks for code. \
Skip filler and preamble.
- You are a chat assistant only: do not use tools or try to read/edit files \
yourself. Your context below includes the workspace file list, the full \
contents of every OPEN editor tab, and the recent terminal history.
- IMPORTANT: you can only see the contents of files marked [open]. If you need \
a file that exists in the workspace but is [not open] — or any file you want to \
reference whose contents you don't have — DO NOT guess or invent its contents. \
Instead tell the user to open it (click it in the Files panel on the left of \
the editor) so you can read it, then continue once it's open.\
"""

_NO_CLI_HELP = (
    "The copilot couldn't find the `claude` CLI. MockSignal drives the copilot "
    "through your local Claude Code install. Install it and make sure `claude` "
    "is on the PATH of whatever shell starts the backend (or set "
    "MOCKSIGNAL_CLAUDE_BIN to its full path), then restart the server."
)

_AUTH_HELP = (
    "The local `claude` CLI isn't logged in (got an authentication error). Run "
    "`claude` once in your terminal and sign in, then restart the backend. "
    "MockSignal reuses that login — no API key needed."
)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... [truncated]"


def _workspace_files(name: Optional[str]) -> List[str]:
    """List the problem folder's files on disk (best-effort, noise filtered)."""
    if not name:
        return []
    try:
        d = problems.problem_dir(name)
    except Exception:  # noqa: BLE001 — unknown problem / IO error: just skip
        return []
    out = []
    for p in sorted(d.iterdir()):
        if p.is_dir() or p.name.startswith(".") or p.suffix == ".pyc":
            continue
        out.append(p.name)
    return out


def _lang_for(name: str) -> str:
    if name.endswith(".py"):
        return "python"
    if name.endswith(".md"):
        return "markdown"
    if name.endswith(".json"):
        return "json"
    return ""


def build_system(ctx: Optional[CopilotContext]) -> str:
    if ctx is None:
        return SYSTEM_BASE
    parts = [SYSTEM_BASE, "\n\n# Current context\n"]
    if ctx.problemTitle:
        parts.append(f"Problem: {ctx.problemTitle}")
    if ctx.activeLevel:
        parts.append(f"Active level tab: Level {ctx.activeLevel}")
    if ctx.description:
        parts.append("\n## Problem description\n" + _truncate(ctx.description, 6000))
    if ctx.levelMarkdown:
        parts.append(
            f"\n## Level {ctx.activeLevel or ''} requirements\n"
            + _truncate(ctx.levelMarkdown, 6000)
        )

    # Normalize open files (fall back to the legacy `code` = solution.py field).
    open_files = list(ctx.openFiles or [])
    if not open_files and ctx.code is not None:
        open_files = [OpenFile(name="solution.py", content=ctx.code)]
    open_names = {f.name for f in open_files}

    # Workspace listing (the folder dir), marking what's open vs not.
    workspace = _workspace_files(ctx.problemName)
    # Include any open file not on disk (shouldn't happen, but be safe).
    for n in open_names:
        if n not in workspace:
            workspace.append(n)
    if workspace:
        listing = "\n".join(
            f"- {n} [{'open' if n in open_names else 'not open'}]"
            for n in sorted(workspace)
        )
        parts.append(
            "\n## Workspace files (problem folder)\n" + listing
            + "\n\nYou see the contents of [open] files below. For any [not open] "
            "file you need, ask the user to open it in the Files panel rather than "
            "guessing its contents."
        )

    # Full contents of every open editor tab.
    for f in open_files:
        body = (f.content or "").strip() or "(empty)"
        parts.append(
            f"\n## Open file: {f.name}\n```{_lang_for(f.name)}\n"
            + _truncate(body, MAX_FILE_CHARS)
            + "\n```"
        )

    if ctx.terminalHistory and ctx.terminalHistory.strip():
        parts.append(
            "\n## Terminal history (recent, may be truncated)\n```\n"
            + _truncate(ctx.terminalHistory.strip(), MAX_TERMINAL_CHARS)
            + "\n```"
        )

    if ctx.lastResults:
        parts.append("\n## Most recent test run\n" + _truncate(ctx.lastResults, 4000))
    return "\n".join(parts)


def _flatten_conversation(messages: List[CopilotMessage]) -> str:
    """`claude -p` is one-shot, so fold the chat into a single prompt.

    A lone user turn is sent verbatim; a multi-turn chat becomes a labelled
    transcript ending on the user's latest message.
    """
    if len(messages) == 1:
        return messages[0].content
    lines = [
        "This is our conversation so far. You are Mio. Continue it by replying "
        "to the final User message.\n"
    ]
    for m in messages:
        who = "User" if m.role == "user" else "Mio"
        lines.append(f"{who}: {m.content}")
    return "\n\n".join(lines)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _is_auth_error(text: str) -> bool:
    low = (text or "").lower()
    return "401" in low or "auth" in low or "credential" in low or "log in" in low


async def stream_reply(body: "CopilotBody") -> AsyncIterator[str]:
    """Yield SSE frames: `token` deltas, then a terminal `done` or `error`."""
    if not CLAUDE_BIN:
        yield _sse("error", {"message": _NO_CLI_HELP})
        return

    history = body.messages[-MAX_HISTORY:]
    if not history or history[-1].role != "user":
        yield _sse("error", {"message": "The last message must come from the user."})
        return

    system = build_system(body.context)
    prompt = _flatten_conversation(history)
    workdir = tempfile.mkdtemp(prefix="mocksignal-copilot-")

    args = [
        CLAUDE_BIN,
        "-p",
        "--system-prompt", system,
        "--model", MODEL,
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--permission-mode", "default",
        "--disallowedTools", *DISALLOWED_TOOLS,
    ]

    proc = None
    # Route stderr to a file rather than a PIPE: we only read it on the
    # no-output path, and an unread PIPE can fill its buffer and deadlock.
    stderr_file = open(os.path.join(workdir, "stderr.log"), "w+b")
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=workdir,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=stderr_file,
        )
        proc.stdin.write(prompt.encode("utf-8"))
        await proc.stdin.drain()
        proc.stdin.close()

        streamed_any = False
        final_text = ""
        error_msg = None

        async def read_events():
            nonlocal streamed_any, final_text, error_msg
            async for raw in proc.stdout:
                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                etype = ev.get("type")
                if etype == "stream_event":
                    inner = ev.get("event", {})
                    if inner.get("type") == "content_block_delta":
                        delta = inner.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            if text:
                                streamed_any = True
                                yield _sse("token", {"text": text})
                elif etype == "assistant":
                    msg = ev.get("message", {})
                    final_text = "".join(
                        b.get("text", "")
                        for b in msg.get("content", [])
                        if b.get("type") == "text"
                    )
                    if ev.get("error"):
                        error_msg = final_text or str(ev.get("error"))
                elif etype == "result":
                    if ev.get("is_error"):
                        error_msg = ev.get("result") or "The copilot run failed."

        try:
            async for frame in _with_timeout(read_events(), OVERALL_TIMEOUT_SECONDS):
                yield frame
        except asyncio.TimeoutError:
            yield _sse(
                "error",
                {"message": "The copilot timed out. Try again, or ask something smaller."},
            )
            return

        await proc.wait()

        if error_msg:
            yield _sse(
                "error",
                {"message": _AUTH_HELP if _is_auth_error(error_msg) else error_msg},
            )
            return

        if not streamed_any:
            if final_text:
                yield _sse("token", {"text": final_text})
            else:
                stderr_file.seek(0)
                stderr = stderr_file.read().decode("utf-8", errors="replace").strip()
                detail = stderr[-500:] if stderr else f"exit code {proc.returncode}"
                yield _sse("error", {"message": f"The copilot produced no output ({detail})."})
                return

        yield _sse("done", {})
    except FileNotFoundError:
        yield _sse("error", {"message": _NO_CLI_HELP})
    except Exception as e:  # noqa: BLE001 — surface anything else to the UI
        yield _sse("error", {"message": f"Unexpected copilot error: {e}"})
    finally:
        if proc and proc.returncode is None:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
        stderr_file.close()
        shutil.rmtree(workdir, ignore_errors=True)


async def _with_timeout(agen: AsyncIterator[str], seconds: float) -> AsyncIterator[str]:
    """Re-yield from an async generator, enforcing a wall-clock deadline."""
    loop = asyncio.get_event_loop()
    deadline = loop.time() + seconds
    ait = agen.__aiter__()
    while True:
        remaining = deadline - loop.time()
        if remaining <= 0:
            raise asyncio.TimeoutError
        try:
            frame = await asyncio.wait_for(ait.__anext__(), timeout=remaining)
        except StopAsyncIteration:
            return
        yield frame
