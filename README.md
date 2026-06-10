# MockSignal

A local, single-user practice environment that mimics the CodeSignal IDE for
drilling Industry Coding Framework (ICF) assessments — three-pane layout,
progressive locked levels, one-click test runs, and an unforgiving overall
timer.

## Setup

Requires Python 3.9+ and Node 18+.

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

## Run

Two processes, two terminals:

```bash
# Terminal 1 — backend (from the repo root, venv activated)
uvicorn backend.main:app --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open the URL Vite prints (http://localhost:5173). The dev server proxies
`/api` to the backend, so you only ever point your browser at one port.

## Using it

1. Pick a problem from the top-bar dropdown.
2. Click **Start session** — the 90-minute timer starts and the editor unlocks.
3. Write your solution in the center pane (it auto-saves to `solution.py`).
4. Click **Run Tests** on the right. Tests are grouped by level; click a
   failed test to see its traceback and failing line.
5. Pass every Level N test to unlock the Level N+1 description tab.
6. **End session** (or run out of time) to lock the editor and see the final
   "X of Y tests passing" score, broken down by level.

The timer never pauses. **Reset solution to stub** (bottom bar) permanently
discards your work after a confirmation.

## Adding problems

Drop a directory into `problems/` — no app code changes needed:

```
problems/
  your_problem/
    description.md       # overview shown above the level tabs
    level1.md            # one markdown file per level
    level2.md
    ...
    solution_stub.py     # starting code; what "Reset" restores
    solution.py          # the working file (auto-saved; created from the stub)
    tests.py             # unittest tests
```

**Convention:** `tests.py` must define `unittest.TestCase` classes named
`TestLevel1`, `TestLevel2`, … — the app uses these names to group results by
level and to gate progression. `tests.py` imports the solution as
`solution` (e.g. `from solution import KVStore`).

### Example: dropping in LibreSignal's Bank System

1. Create `problems/bank_system/`.
2. Copy in the files, renaming `simulation.py` → `solution_stub.py` (and
   `solution.py`) and `test_bank_system.py` → `tests.py`.
3. Split the existing markdown into `level1.md` … `level4.md` and write a
   short `description.md`.
4. Restart nothing — just reselect the problem in the dropdown.

## Panels

- **File navigator** — the `Files` pane lists the problem's files. Click to
  open them as editor tabs: `solution.py` is editable, `tests.py` opens
  read-only (you can read the tests, not change them).
- **Resizable** — drag any separator between panes (description / files /
  editor / bottom pane) to resize.
- **Backups** — every save snapshots the previous `solution.py` into the
  problem's `.backups/` directory (throttled; the 80 most-recent are kept).
  The bottom-bar **Backups** menu lists them and restores any one — and
  snapshots the current file first, so a restore is itself reversible.

## Terminal

The bottom pane has **Terminal** tabs — real PTY-backed shells (xterm.js ↔ a
WebSocket) rooted in the active problem's directory. Add one with `+`, remove
one with the trash icon; each is an independent shell. Use it to debug with
`pdb`:

```
python3 -m pdb tests.py        # step through the tests
python3 -m pdb solution.py     # step through your solution
```

The project's `.venv` is put first on `PATH`, so `python`/`pdb` match the
interpreter the test runner uses. It's a normal shell with your privileges —
fine for a single-user local tool.

## How tests run

`Run Tests` POSTs to the backend, which runs `backend/harness.py` in a
subprocess against the problem directory. The harness runs each `unittest`
test individually and streams structured JSON events as each one completes:
per-test status, traceback, failing line number, and captured stdout/stderr.

Each test has a **10-second per-test budget** (SIGALRM); a single slow or
deadlocked test is marked `timeout` and the run moves on to the next.
The whole run has a **30-second overall budget**; if it fires, the harness
is killed as a process group but the records reported so far are still
returned — so a slow test late in the run never erases earlier results.
Tests always run against the saved `solution.py` on disk — auto-save flushes
the editor buffer before each run.

## Layout

```
backend/
  main.py        FastAPI routes (REST + the terminal WebSocket)
  problems.py    problem discovery + file I/O
  runner.py      subprocess runner with timeout
  harness.py     unittest harness → structured JSON (runs as a subprocess)
  terminal.py    PTY-backed shell bridged over a WebSocket
frontend/
  src/
    App.jsx              top-level wiring + layout
    hooks/useSession.js  session state (useReducer)
    lib/                 api client + grading/gating helpers
    components/          TopBar, Sidebar, ProblemPanel, FilesPanel,
                         EditorPane, BottomPane (TestResults + Terminal), ...
problems/
  demo_kvstore/  built-in demo problem
```

## License

MockSignal's own code and original practice problems are released under the
[MIT License](LICENSE).

Some problems (Bank System, In-Memory Database) are imported from
[LibreSignal](https://github.com/EricZheng0404/LibreSignal) and remain the
property of their original author; see [NOTICE](NOTICE) for details.

MockSignal is an independent tool and is not affiliated with or endorsed by
CodeSignal, Inc.
