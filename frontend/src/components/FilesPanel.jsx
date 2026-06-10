import { PyChip, LockIcon } from './icons'

// File navigator. Lists the problem's files; clicking one opens it as an
// editor tab. solution.py is editable; tests.py opens read-only.
export default function FilesPanel({ files, activeFile, onOpen }) {
  return (
    <div className="flex h-full w-full flex-col bg-ink-850">
      <div className="border-b border-ink-700 px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-ink-400">
        Files
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto py-1">
        {files.length === 0 ? (
          <p className="px-3 py-2 text-xs text-ink-400">No files.</p>
        ) : (
          files.map((f) => {
            const isActive = f.name === activeFile
            return (
              <button
                key={f.name}
                onClick={() => onOpen(f.name)}
                className={[
                  'flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs',
                  isActive
                    ? 'bg-accent/20 text-ink-100'
                    : 'text-ink-300 hover:bg-ink-800',
                ].join(' ')}
              >
                <PyChip />
                <span className="truncate font-mono">{f.name}</span>
                {!f.editable && <LockIcon className="ml-auto text-ink-400" />}
              </button>
            )
          })
        )}
      </div>
    </div>
  )
}
