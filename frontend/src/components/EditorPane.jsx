import Editor from '@monaco-editor/react'
import { PyChip, LockIcon, CloseIcon } from './icons'

// A navy Monaco theme so the editor matches the rest of the IDE.
function defineTheme(monaco) {
  monaco.editor.defineTheme('mocksignal', {
    base: 'vs-dark',
    inherit: true,
    rules: [],
    colors: {
      'editor.background': '#1a2138',
      'editor.lineHighlightBackground': '#212a47',
      'editorLineNumber.foreground': '#46506f',
      'editorLineNumber.activeForeground': '#9aa3bd',
      'editorGutter.background': '#1a2138',
      'editor.selectionBackground': '#2f3e6b',
      'editorCursor.foreground': '#4d82ff',
      'editorWidget.background': '#212a47',
      'editorWidget.border': '#2f3a63',
      'editorSuggestWidget.background': '#212a47',
      'editorIndentGuide.background1': '#2a3350',
      'editorIndentGuide.activeBackground1': '#3d4a77',
    },
  })
}

const EDITOR_OPTIONS = {
  fontSize: 13,
  minimap: { enabled: true },
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 4,
  renderWhitespace: 'selection',
  padding: { top: 10 },
}

// Center pane: one Monaco editor per open file. Inactive editors are hidden,
// not unmounted, so each file keeps its own folds / scroll / cursor / undo.
// Editors are uncontrolled (defaultValue): Monaco owns the text while typing,
// so React never re-applies a stale value and bumps the cursor. solution.py's
// editor is remounted on reset/restore via the reloadKey.
export default function EditorPane({
  problemName,
  openFiles, // [{ name, editable, content }]
  activeFile,
  reloadKey,
  sessionLocked,
  saving,
  dirty,
  onSelectFile,
  onCloseFile,
  onChange,
}) {
  const activeMeta =
    openFiles.find((f) => f.name === activeFile) ?? { editable: false }

  let status = 'Saved'
  let statusColor = 'text-emerald-400'
  if (!activeMeta.editable || sessionLocked) {
    status = 'read-only'
    statusColor = 'text-ink-400'
  } else if (saving) {
    status = 'Saving…'
    statusColor = 'text-ink-300'
  } else if (dirty) {
    status = 'Unsaved'
    statusColor = 'text-amber-400'
  }

  return (
    <main className="flex min-w-0 flex-1 flex-col bg-ink-850">
      <div className="flex items-stretch border-b border-ink-700 bg-ink-900">
        <div className="flex min-w-0 flex-1 items-stretch overflow-x-auto">
          {openFiles.map((f) => {
            const isActive = f.name === activeFile
            const closeable = f.name !== 'solution.py'
            return (
              <div
                key={f.name}
                onClick={() => onSelectFile(f.name)}
                className={[
                  'flex shrink-0 cursor-pointer items-center gap-2 border-r border-t-2 border-r-ink-700 px-3 py-1.5 text-xs',
                  isActive
                    ? 'border-t-accent bg-ink-850 text-ink-100'
                    : 'border-t-transparent text-ink-400 hover:text-ink-200',
                ].join(' ')}
              >
                <PyChip />
                <span className="font-mono">{f.name}</span>
                {!f.editable && <LockIcon className="text-ink-400" />}
                {closeable && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onCloseFile(f.name)
                    }}
                    title="Close tab"
                    className="ml-0.5 rounded p-0.5 text-ink-400 hover:bg-ink-700 hover:text-ink-100"
                  >
                    <CloseIcon />
                  </button>
                )}
              </div>
            )
          })}
        </div>
        <div className="flex shrink-0 items-center gap-2.5 px-3 text-[11px]">
          <span className={statusColor}>{status}</span>
          <span className="text-ink-700">|</span>
          <span className="text-ink-400">Python 3 &middot; unittest</span>
        </div>
      </div>

      <div className="min-h-0 flex-1">
        {openFiles.map((f) => {
          const isActive = f.name === activeFile
          // Only solution.py changes outside the editor (reset/restore), so
          // only it carries the reloadKey that forces a fresh editor.
          const editorKey =
            f.name === 'solution.py'
              ? `${problemName ?? 'none'}::solution.py::${reloadKey}`
              : `${problemName ?? 'none'}::${f.name}`
          return (
            <div key={f.name} className={isActive ? 'h-full' : 'hidden'}>
              <Editor
                key={editorKey}
                language="python"
                theme="mocksignal"
                beforeMount={defineTheme}
                defaultValue={f.content}
                onChange={
                  f.editable ? (value) => onChange(value ?? '') : undefined
                }
                options={{
                  ...EDITOR_OPTIONS,
                  readOnly: !f.editable || sessionLocked,
                }}
              />
            </div>
          )
        })}
      </div>
    </main>
  )
}
