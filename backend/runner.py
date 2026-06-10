"""Streams the harness's per-test events back as a structured result.

Each test record arrives as it completes, so a slow test late in the run
does not erase the earlier results — when the overall timeout fires, every
record reported so far is still returned to the UI.
"""
from __future__ import annotations

import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

HARNESS = Path(__file__).resolve().parent / "harness.py"
TIMEOUT_SECONDS = 30


def run_tests(problem_dir: Path) -> dict:
    started = time.time()
    try:
        proc = subprocess.Popen(
            [sys.executable, "-u", str(HARNESS), str(problem_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
    except OSError as e:
        return _meta({"status": "error", "message": str(e), "tests": []}, started)

    # A reader thread pushes each stdout line onto a queue so the main loop
    # can wait with a timeout.
    events: queue.Queue = queue.Queue()

    def reader():
        try:
            for line in iter(proc.stdout.readline, ""):
                events.put(("line", line))
        finally:
            events.put(("eof", None))

    threading.Thread(target=reader, daemon=True).start()

    records: list[dict] = []
    in_flight = None
    status = "ok"
    message = ""
    coll_tb = ""

    deadline = started + TIMEOUT_SECONDS
    while True:
        remaining = deadline - time.time()
        if remaining <= 0:
            status = "timeout"
            message = (
                f"Test run exceeded {TIMEOUT_SECONDS}s overall "
                "— earlier results are below."
            )
            break
        try:
            kind, data = events.get(timeout=remaining)
        except queue.Empty:
            status = "timeout"
            message = f"Test run exceeded {TIMEOUT_SECONDS}s overall."
            break

        if kind == "eof":
            break

        try:
            ev = json.loads(data.strip())
        except (json.JSONDecodeError, ValueError):
            continue

        e = ev.get("event")
        if e == "start":
            in_flight = ev
        elif e == "test":
            records.append(ev.get("record", {}))
            in_flight = None
        elif e == "done":
            in_flight = None
            break
        elif e == "collection_error":
            status = "collection_error"
            message = ev.get("message", "")
            coll_tb = ev.get("traceback", "")
            # harness will exit; loop will see eof and break
        elif e == "error":
            status = "error"
            message = ev.get("message", "")

    if status == "timeout":
        _kill_group(proc)
        if in_flight:
            records.append({
                "id": in_flight.get("id", "?"),
                "class": in_flight.get("class", "?"),
                "method": in_flight.get("method", "?"),
                "level": in_flight.get("level"),
                "status": "timeout",
                "message": (
                    f"Test killed: exceeded the overall {TIMEOUT_SECONDS}s "
                    "run budget."
                ),
                "traceback": "",
                "line": None,
                "stdout": "",
                "stderr": "",
            })

    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass

    out = {"status": status, "tests": records}
    if message:
        out["message"] = message
    if coll_tb:
        out["traceback"] = coll_tb
    return _meta(out, started)


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            proc.kill()
        except ProcessLookupError:
            pass


def _meta(data: dict, started: float) -> dict:
    data.setdefault("tests", [])
    data["durationMs"] = int((time.time() - started) * 1000)
    data["ranAt"] = time.strftime("%H:%M:%S")
    return data
