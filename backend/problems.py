"""Discovery and file I/O for problems that live on disk under ``problems/``.

A problem is any directory under ``problems/`` that contains a ``tests.py``.
Everything else (level markdown, stub, solution) is optional but expected.
"""
from __future__ import annotations

import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = REPO_ROOT / "problems"


class ProblemNotFound(Exception):
    """Raised when a requested problem name does not resolve to a directory."""


def _is_problem(p: Path) -> bool:
    return p.is_dir() and (p / "tests.py").exists()


def problem_dir(name: str) -> Path:
    """Resolve a problem name to its directory, rejecting path traversal."""
    if not name or "/" in name or "\\" in name or name in (".", ".."):
        raise ProblemNotFound(f"Unknown problem: {name!r}")
    p = (PROBLEMS_DIR / name).resolve()
    if p.parent != PROBLEMS_DIR.resolve() or not _is_problem(p):
        raise ProblemNotFound(f"Unknown problem: {name!r}")
    return p


def _title(p: Path) -> str:
    """Use the first markdown heading of description.md, else the dir name."""
    desc = p / "description.md"
    if desc.exists():
        for line in desc.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()
    return p.name.replace("_", " ").title()


def list_problems() -> list[dict]:
    if not PROBLEMS_DIR.exists():
        return []
    return [
        {"name": p.name, "title": _title(p)}
        for p in sorted(PROBLEMS_DIR.iterdir())
        if _is_problem(p)
    ]


def _levels(p: Path) -> list[dict]:
    """Read level{1,2,3,...}.md until the numbering stops."""
    levels = []
    n = 1
    while (p / f"level{n}.md").exists():
        levels.append(
            {"level": n, "markdown": (p / f"level{n}.md").read_text(encoding="utf-8")}
        )
        n += 1
    return levels


def get_problem(name: str) -> dict:
    p = problem_dir(name)
    desc = p / "description.md"
    levels = _levels(p)
    return {
        "name": name,
        "title": _title(p),
        "description": desc.read_text(encoding="utf-8") if desc.exists() else "",
        "levels": levels,
        "levelCount": len(levels),
    }


def read_solution(name: str) -> str:
    """Return solution.py, seeding it from the stub on first access."""
    p = problem_dir(name)
    sol = p / "solution.py"
    if not sol.exists():
        stub = p / "solution_stub.py"
        seed = stub.read_text(encoding="utf-8") if stub.exists() else ""
        sol.write_text(seed, encoding="utf-8")
    return sol.read_text(encoding="utf-8")


BACKUP_DIRNAME = ".backups"
BACKUP_MIN_INTERVAL_SECONDS = 30  # at most one snapshot per this many seconds on saves
MAX_BACKUPS = 80                  # most-recent snapshots kept per problem


def _snapshot(problem_path: Path, force: bool = False) -> None:
    """Copy the current solution.py into .backups/ before it is overwritten.

    Throttled on ordinary saves; ``force=True`` (reset/restore) always snapshots.
    """
    sol = problem_path / "solution.py"
    if not sol.exists():
        return
    current = sol.read_text(encoding="utf-8")
    if not current.strip():
        return
    backups = problem_path / BACKUP_DIRNAME
    backups.mkdir(exist_ok=True)
    existing = sorted(backups.glob("solution.*.py"))
    if existing:
        newest = existing[-1]
        if newest.read_text(encoding="utf-8") == current:
            return  # this exact content is already the newest backup
        age = time.time() - newest.stat().st_mtime
        if not force and age < BACKUP_MIN_INTERVAL_SECONDS:
            return
    stamp = time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}"
    (backups / f"solution.{stamp}.py").write_text(current, encoding="utf-8")
    for old in sorted(backups.glob("solution.*.py"))[:-MAX_BACKUPS]:
        old.unlink()


def write_solution(name: str, content: str) -> None:
    p = problem_dir(name)
    _snapshot(p)  # snapshot the pre-write state (throttled)
    (p / "solution.py").write_text(content, encoding="utf-8")


def reset_solution(name: str) -> str:
    """Overwrite solution.py with the stub and return the new content."""
    p = problem_dir(name)
    _snapshot(p, force=True)  # a reset is destructive — always snapshot first
    stub = p / "solution_stub.py"
    content = stub.read_text(encoding="utf-8") if stub.exists() else ""
    (p / "solution.py").write_text(content, encoding="utf-8")
    return content


# Files surfaced in the in-app file navigator, with whether they are editable.
# solution.py is the working file; tests.py is shown read-only so the solver
# can read the tests (as on the real assessment) but not change them.
NAVIGATOR_FILES = (
    ("solution.py", True),
    ("tests.py", False),
)


def list_files(name: str) -> list[dict]:
    p = problem_dir(name)
    out = []
    for fname, editable in NAVIGATOR_FILES:
        if fname == "solution.py" or (p / fname).exists():
            out.append({"name": fname, "editable": editable})
    return out


def read_file(name: str, filename: str) -> dict:
    """Return {content, editable} for a navigator file, else raise."""
    editable_by_name = dict(NAVIGATOR_FILES)
    if filename not in editable_by_name:
        raise ProblemNotFound(f"No such file: {filename!r}")
    if filename == "solution.py":
        return {"content": read_solution(name), "editable": True}
    target = problem_dir(name) / filename
    if not target.exists():
        raise ProblemNotFound(f"No such file: {filename!r}")
    return {
        "content": target.read_text(encoding="utf-8"),
        "editable": editable_by_name[filename],
    }


def list_backups(name: str) -> list[dict]:
    """Most-recent-first list of solution.py snapshots for a problem."""
    backups = problem_dir(name) / BACKUP_DIRNAME
    if not backups.is_dir():
        return []
    out = []
    for f in sorted(backups.glob("solution.*.py"), reverse=True):
        st = f.stat()
        out.append({"id": f.name, "savedAt": st.st_mtime, "size": st.st_size})
    return out


def restore_backup(name: str, backup_id: str) -> str:
    """Restore solution.py from a backup, snapshotting the current file first."""
    p = problem_dir(name)
    backups = p / BACKUP_DIRNAME
    if (
        not backup_id.startswith("solution.")
        or not backup_id.endswith(".py")
        or "/" in backup_id
        or "\\" in backup_id
        or ".." in backup_id
    ):
        raise ProblemNotFound(f"Unknown backup: {backup_id!r}")
    target = backups / backup_id
    if not target.is_file() or target.resolve().parent != backups.resolve():
        raise ProblemNotFound(f"Unknown backup: {backup_id!r}")
    content = target.read_text(encoding="utf-8")
    _snapshot(p, force=True)  # so a restore is itself reversible
    (p / "solution.py").write_text(content, encoding="utf-8")
    return content
