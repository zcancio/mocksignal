"""Runs a problem's test suite and emits structured JSON events on stdout.

Each test reports incrementally as a one-line JSON object::

    {"event": "start", "id", "class", "method", "level"}   -- before a test runs
    {"event": "test", "record": {...}}                      -- after a test finishes
    {"event": "done"}                                        -- all tests completed
    {"event": "collection_error", "message", "traceback"}   -- load failed

Streaming lets ``runner.py`` return partial results when a slow test late in
the run blows the overall timeout — earlier results are already captured.

Each test also has its own per-test timeout via SIGALRM: a single slow or
deadlocked test is marked ``timeout`` and the run continues with the next.
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import signal
import sys
import traceback
import unittest

LEVEL_RE = re.compile(r"TestLevel(\d+)", re.IGNORECASE)
FRAME_RE = re.compile(r'File "([^"]*)", line (\d+)')
HARNESS_PATH = os.path.abspath(__file__)
PER_TEST_TIMEOUT_SECONDS = 10


class _PerTestTimeout(KeyboardInterrupt):
    """Raised by the SIGALRM handler. KeyboardInterrupt-derived so unittest's
    bare ``except`` re-raises it instead of recording it as a normal error."""


def _alarm(_signum, _frame):
    raise _PerTestTimeout()


def load_tests(problem_dir):
    """Import tests.py from the problem directory as the module ``tests``."""
    path = os.path.join(problem_dir, "tests.py")
    spec = importlib.util.spec_from_file_location("tests", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["tests"] = module
    spec.loader.exec_module(module)
    return module


def iter_tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from iter_tests(item)
        else:
            yield item


def level_of(name):
    m = LEVEL_RE.search(name)
    return int(m.group(1)) if m else None


def fail_line(tb, problem_dir):
    """Return the deepest traceback line that points inside the problem dir."""
    problem_dir = os.path.abspath(problem_dir)
    best = None
    for m in FRAME_RE.finditer(tb):
        if os.path.abspath(m.group(1)).startswith(problem_dir):
            best = int(m.group(2))
    if best is not None:
        return best
    frames = FRAME_RE.findall(tb)
    return int(frames[-1][1]) if frames else None


def clean_tb(tb):
    """Drop traceback frames that point at this harness file itself."""
    lines = tb.splitlines(keepends=True)
    kept, i = [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith('File "') and HARNESS_PATH in lines[i]:
            i += 2
            continue
        kept.append(lines[i])
        i += 1
    return "".join(kept)


def make_record(cls_name, method, status, message, tb, out, err, problem_dir):
    if tb and not message:
        nonblank = [ln for ln in tb.strip().splitlines() if ln.strip()]
        message = nonblank[-1] if nonblank else ""
    return {
        "id": f"{cls_name}.{method}",
        "class": cls_name,
        "method": method,
        "level": level_of(cls_name),
        "status": status,
        "message": message,
        "traceback": tb,
        "line": fail_line(tb, problem_dir) if tb else None,
        "stdout": out,
        "stderr": err,
    }


def _timeout_record(cls, method, problem_dir):
    return {
        "id": f"{cls}.{method}",
        "class": cls,
        "method": method,
        "level": level_of(cls),
        "status": "timeout",
        "message": f"Test exceeded the {PER_TEST_TIMEOUT_SECONDS}s per-test budget.",
        "traceback": "",
        "line": None,
        "stdout": "",
        "stderr": "",
    }


def run_unittest_case(test, problem_dir):
    result = unittest.TestResult()
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            test(result)
        except Exception:  # pragma: no cover - defensive
            pass
    status, message, tb = "pass", "", ""
    if result.errors:
        status, tb = "error", result.errors[0][1]
    elif result.failures:
        status, tb = "fail", result.failures[0][1]
    elif result.skipped:
        status, message = "skip", result.skipped[0][1]
    return make_record(
        type(test).__name__,
        getattr(test, "_testMethodName", str(test)),
        status, message, tb, out.getvalue(), err.getvalue(), problem_dir,
    )


def run_plain_method(cls, cls_name, method_name, problem_dir):
    out, err = io.StringIO(), io.StringIO()
    status, message, tb = "pass", "", ""
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            getattr(cls(), method_name)()
        except AssertionError:
            status, tb = "fail", clean_tb(traceback.format_exc())
        except unittest.SkipTest as e:
            status, message = "skip", str(e)
        except Exception:
            status, tb = "error", clean_tb(traceback.format_exc())
    return make_record(
        cls_name, method_name, status, message, tb,
        out.getvalue(), err.getvalue(), problem_dir,
    )


def emit(event):
    print(json.dumps(event), flush=True)


def _run_with_timeout(fn, cls, method, problem_dir):
    """Run ``fn()`` with the per-test SIGALRM timeout."""
    signal.setitimer(signal.ITIMER_REAL, PER_TEST_TIMEOUT_SECONDS)
    try:
        return fn()
    except _PerTestTimeout:
        return _timeout_record(cls, method, problem_dir)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main():
    if len(sys.argv) < 2:
        emit({"event": "error", "message": "no problem dir"})
        return

    problem_dir = os.path.abspath(sys.argv[1])
    sys.path.insert(0, problem_dir)
    os.chdir(problem_dir)

    signal.signal(signal.SIGALRM, _alarm)

    try:
        module = load_tests(problem_dir)
        suite = unittest.TestLoader().loadTestsFromModule(module)
    except Exception:
        emit({
            "event": "collection_error",
            "message": "tests.py could not be loaded (syntax error or bad import).",
            "traceback": traceback.format_exc(),
        })
        return

    # 1. unittest.TestCase subclasses.
    for test in iter_tests(suite):
        cls = type(test).__name__
        method = getattr(test, "_testMethodName", str(test))
        emit({"event": "start", "id": f"{cls}.{method}",
              "class": cls, "method": method, "level": level_of(cls)})
        rec = _run_with_timeout(
            lambda: run_unittest_case(test, problem_dir),
            cls, method, problem_dir,
        )
        emit({"event": "test", "record": rec})

    # 2. Plain pytest-style TestLevelN classes (bare assert, no unittest base).
    for name, obj in vars(module).items():
        if not isinstance(obj, type) or LEVEL_RE.search(name) is None:
            continue
        if issubclass(obj, unittest.TestCase):
            continue
        for meth_name, meth in vars(obj).items():
            if meth_name.startswith("test") and callable(meth):
                emit({"event": "start", "id": f"{name}.{meth_name}",
                      "class": name, "method": meth_name,
                      "level": level_of(name)})
                rec = _run_with_timeout(
                    lambda obj=obj, name=name, meth=meth_name:
                        run_plain_method(obj, name, meth, problem_dir),
                    name, meth_name, problem_dir,
                )
                emit({"event": "test", "record": rec})

    emit({"event": "done"})


if __name__ == "__main__":
    main()
