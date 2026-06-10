import { useRef, useState } from 'react'
import TestResults from './TestResults'
import Terminal from './Terminal'

function PlayIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 12 12" fill="currentColor" aria-hidden>
      <path d="M2.5 1.4v9.2L10 6z" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3" />
    </svg>
  )
}

// Bottom pane: a Unit Tests tab plus any number of real terminals (add with
// +, remove with the trash icon). Each terminal is an independent shell.
export default function BottomPane({
  problemName,
  results,
  running,
  canRun,
  levelCount,
  onRun,
  resizeKey,
}) {
  const [tab, setTab] = useState('tests')
  const [terminals, setTerminals] = useState([{ id: 1 }])
  const nextId = useRef(2)

  const addTerminal = () => {
    const id = nextId.current
    nextId.current += 1
    setTerminals((t) => [...t, { id }])
    setTab(id)
  }

  const closeTerminal = (id) => {
    setTerminals((prev) => prev.filter((x) => x.id !== id))
    setTab((cur) => {
      if (cur !== id) return cur
      const rest = terminals.filter((x) => x.id !== id)
      return rest.length ? rest[rest.length - 1].id : 'tests'
    })
  }

  const run = () => {
    setTab('tests')
    onRun()
  }

  return (
    <div className="flex h-full flex-col border-t border-ink-700 bg-ink-850">
      <div className="flex items-stretch border-b border-ink-700 bg-ink-900">
        <button
          onClick={() => setTab('tests')}
          className={[
            'border-t-2 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider transition-colors',
            tab === 'tests'
              ? 'border-accent bg-ink-850 text-ink-100'
              : 'border-transparent text-ink-400 hover:text-ink-200',
          ].join(' ')}
        >
          Unit Tests
        </button>

        {terminals.map((t, i) => {
          const active = tab === t.id
          return (
            <div
              key={t.id}
              className={[
                'flex items-center border-t-2 transition-colors',
                active ? 'border-accent bg-ink-850' : 'border-transparent',
              ].join(' ')}
            >
              <button
                onClick={() => setTab(t.id)}
                className={`py-1.5 pl-4 pr-1 text-xs font-semibold uppercase tracking-wider ${
                  active ? 'text-ink-100' : 'text-ink-400 hover:text-ink-200'
                }`}
              >
                Terminal {i + 1}
              </button>
              <button
                onClick={() => closeTerminal(t.id)}
                title="Close terminal"
                className="mr-1.5 rounded p-0.5 text-ink-400 hover:bg-ink-700 hover:text-ink-100"
              >
                <TrashIcon />
              </button>
            </div>
          )
        })}

        <button
          onClick={addTerminal}
          title="New terminal"
          className="border-t-2 border-transparent px-2.5 pb-0.5 text-base font-semibold text-ink-400 hover:text-ink-100"
        >
          +
        </button>

        <div className="ml-auto flex items-center pr-2">
          <button
            onClick={run}
            disabled={!canRun || running}
            className="flex items-center gap-1.5 rounded bg-accent px-3.5 py-1.5 text-xs font-bold uppercase tracking-wide text-white hover:bg-accent-bright disabled:cursor-not-allowed disabled:opacity-40"
          >
            <PlayIcon />
            {running ? 'Running…' : 'Run Tests'}
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1">
        <div className={tab === 'tests' ? 'h-full' : 'hidden'}>
          <TestResults
            results={results}
            canRun={canRun}
            levelCount={levelCount}
          />
        </div>
        {terminals.map((t) => (
          <div key={t.id} className={tab === t.id ? 'h-full' : 'hidden'}>
            <Terminal
              problemName={problemName}
              active={tab === t.id}
              resizeKey={resizeKey}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
