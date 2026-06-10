// Thin wrapper over the backend REST API. All paths are proxied to :8000
// by the Vite dev server.

async function json(res) {
  if (!res.ok) {
    let detail = res.statusText
    try {
      detail = (await res.json()).detail ?? detail
    } catch {
      /* response had no JSON body */
    }
    throw new Error(`${res.status}: ${detail}`)
  }
  return res.json()
}

export const api = {
  config: () => fetch('/api/config').then(json),

  listProblems: () => fetch('/api/problems').then(json),

  getProblem: (name) => fetch(`/api/problems/${name}`).then(json),

  getSolution: (name) => fetch(`/api/problems/${name}/solution`).then(json),

  saveSolution: (name, content) =>
    fetch(`/api/problems/${name}/solution`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    }).then(json),

  runTests: (name) =>
    fetch(`/api/problems/${name}/run`, { method: 'POST' }).then(json),

  reset: (name) =>
    fetch(`/api/problems/${name}/reset`, { method: 'POST' }).then(json),

  listFiles: (name) => fetch(`/api/problems/${name}/files`).then(json),

  getFile: (name, filename) =>
    fetch(`/api/problems/${name}/files/${filename}`).then(json),

  listBackups: (name) => fetch(`/api/problems/${name}/backups`).then(json),

  restoreBackup: (name, id) =>
    fetch(`/api/problems/${name}/backups/${id}/restore`, {
      method: 'POST',
    }).then(json),
}
