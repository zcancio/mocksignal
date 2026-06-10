import { useState } from 'react'
import { api } from '../lib/api'

function fmt(savedAt) {
  const d = new Date(savedAt * 1000)
  const time = d.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
  const age = Math.max(0, Math.floor(Date.now() / 1000 - savedAt))
  let rel
  if (age < 60) rel = `${age}s ago`
  else if (age < 3600) rel = `${Math.floor(age / 60)}m ago`
  else if (age < 86400) rel = `${Math.floor(age / 3600)}h ago`
  else rel = `${Math.floor(age / 86400)}d ago`
  return { time, rel }
}

// Bottom-bar menu that lists solution.py snapshots and restores one.
export default function BackupsMenu({ problemName, onRestored }) {
  const [open, setOpen] = useState(false)
  const [backups, setBackups] = useState(null) // null = loading

  const toggle = async () => {
    if (open) {
      setOpen(false)
      return
    }
    setOpen(true)
    setBackups(null)
    try {
      setBackups(await api.listBackups(problemName))
    } catch (e) {
      console.error('Could not list backups', e)
      setBackups([])
    }
  }

  const restore = async (id) => {
    const ok = window.confirm(
      'Restore this backup?\n\n' +
        'Your current solution.py is snapshotted first, so this is reversible.',
    )
    if (!ok) return
    try {
      const { content } = await api.restoreBackup(problemName, id)
      onRestored(content)
      setOpen(false)
    } catch (e) {
      console.error('Restore failed', e)
    }
  }

  return (
    <div className="relative">
      <button
        onClick={toggle}
        disabled={!problemName}
        className="rounded border border-ink-700 px-2 py-0.5 text-ink-300 hover:bg-ink-800 hover:text-ink-100 disabled:opacity-40"
      >
        Backups
      </button>
      {open && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
          />
          <div className="absolute bottom-full right-0 z-20 mb-1 max-h-72 w-64 overflow-y-auto rounded border border-ink-700 bg-ink-850 shadow-xl">
            <div className="border-b border-ink-700 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-ink-400">
              Solution backups
            </div>
            {backups === null && (
              <div className="px-3 py-2 text-ink-400">Loading…</div>
            )}
            {backups?.length === 0 && (
              <div className="px-3 py-2 text-ink-400">
                No backups yet — they&rsquo;re created as you work.
              </div>
            )}
            {backups?.map((b) => {
              const { time, rel } = fmt(b.savedAt)
              return (
                <button
                  key={b.id}
                  onClick={() => restore(b.id)}
                  className="flex w-full items-center justify-between gap-2 px-3 py-1.5 text-left hover:bg-ink-750"
                >
                  <span className="font-mono text-ink-200">{time}</span>
                  <span className="text-ink-400">{rel}</span>
                </button>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
