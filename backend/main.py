"""MockSignal backend: a thin FastAPI layer over problem files on disk."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import problems
from .runner import run_tests
from .terminal import terminal_session

DEFAULT_TIMER_MINUTES = 90

app = FastAPI(title="MockSignal")

# The frontend is normally same-origin via the Vite proxy; this just allows
# hitting the backend directly during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SolutionBody(BaseModel):
    content: str


def _problem_or_404(name: str):
    try:
        return problems.problem_dir(name)
    except problems.ProblemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/config")
def get_config():
    return {"defaultTimerMinutes": DEFAULT_TIMER_MINUTES}


@app.get("/api/problems")
def list_problems():
    return problems.list_problems()


@app.get("/api/problems/{name}")
def get_problem(name: str):
    _problem_or_404(name)
    return problems.get_problem(name)


@app.get("/api/problems/{name}/solution")
def get_solution(name: str):
    _problem_or_404(name)
    return {"content": problems.read_solution(name)}


@app.put("/api/problems/{name}/solution")
def put_solution(name: str, body: SolutionBody):
    _problem_or_404(name)
    problems.write_solution(name, body.content)
    return {"ok": True}


@app.post("/api/problems/{name}/reset")
def reset_solution(name: str):
    _problem_or_404(name)
    return {"content": problems.reset_solution(name)}


@app.get("/api/problems/{name}/backups")
def list_backups(name: str):
    _problem_or_404(name)
    return problems.list_backups(name)


@app.post("/api/problems/{name}/backups/{backup_id}/restore")
def restore_backup(name: str, backup_id: str):
    _problem_or_404(name)
    try:
        return {"content": problems.restore_backup(name, backup_id)}
    except problems.ProblemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/problems/{name}/files")
def list_files(name: str):
    _problem_or_404(name)
    return problems.list_files(name)


@app.get("/api/problems/{name}/files/{filename}")
def read_file(name: str, filename: str):
    _problem_or_404(name)
    try:
        return problems.read_file(name, filename)
    except problems.ProblemNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/problems/{name}/run")
def run(name: str):
    return run_tests(_problem_or_404(name))


@app.websocket("/api/problems/{name}/terminal")
async def terminal(websocket: WebSocket, name: str):
    try:
        cwd = problems.problem_dir(name)
    except problems.ProblemNotFound:
        await websocket.close(code=1008)
        return
    await terminal_session(websocket, cwd)
