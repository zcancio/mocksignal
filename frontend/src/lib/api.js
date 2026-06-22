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

  // Stream a copilot reply. Calls onToken(text) for each delta and resolves
  // when the stream ends; rejects (or calls onToken with an error) on failure.
  // Returns an AbortController so the caller can cancel an in-flight reply.
  copilot: ({ messages, context }, { onToken, onError, signal } = {}) =>
    streamCopilot({ messages, context }, { onToken, onError, signal }),
}

async function streamCopilot({ messages, context }, { onToken, onError, signal }) {
  const res = await fetch('/api/copilot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, context }),
    signal,
  })
  if (!res.ok || !res.body) {
    onError?.(new Error(`Copilot request failed (${res.status})`))
    return
  }

  // Parse the SSE byte stream into `event:`/`data:` frames.
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  const dispatch = (frame) => {
    const lines = frame.split('\n')
    let event = 'message'
    let data = ''
    for (const line of lines) {
      if (line.startsWith('event:')) event = line.slice(6).trim()
      else if (line.startsWith('data:')) data += line.slice(5).trim()
    }
    if (!data) return
    const payload = JSON.parse(data)
    if (event === 'token') onToken?.(payload.text)
    else if (event === 'error') onError?.(new Error(payload.message))
  }

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let sep
    while ((sep = buffer.indexOf('\n\n')) !== -1) {
      const frame = buffer.slice(0, sep)
      buffer = buffer.slice(sep + 2)
      if (frame.trim()) dispatch(frame)
    }
  }
}
