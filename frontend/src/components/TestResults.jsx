import { useState } from 'react'

const DOT = {
  pass: 'bg-emerald-500',
  fail: 'bg-red-500',
  error: 'bg-orange-500',
  skip: 'bg-ink-600',
}
const LABEL = {
  pass: 'text-emerald-400',
  fail: 'text-red-400',
  error: 'text-orange-400',
  skip: 'text-ink-400',
}

function TestRow({ test }) {
  const [open, setOpen] = useState(false)
  const expandable = test.status === 'fail' || test.status === 'error'
  return (
    <li className="border-b border-ink-700/50">
      <button
        onClick={() => expandable && setOpen((o) => !o)}
        className={`flex w-full items-center gap-2 px-3 py-1.5 text-left ${
          expandable ? 'hover:bg-ink-750' : 'cursor-default'
        }`}
      >
        <span
          className={`h-2 w-2 shrink-0 rounded-full ${DOT[test.status] ?? DOT.skip}`}
        />
        <span className="truncate font-mono text-xs text-ink-300">
          {test.method}
        </span>
        <span className={`ml-auto text-xs ${LABEL[test.status] ?? LABEL.skip}`}>
          {test.status}
        </span>
      </button>
      {open && expandable && (
        <div className="bg-ink-950 px-3 py-2">
          {test.line != null && (
            <div className="mb-1 text-xs text-ink-400">
              Failed at line {test.line}
            </div>
          )}
          <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-ink-300">
            {test.traceback || test.message}
          </pre>
          {test.stdout ? (
            <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs text-ink-400">
              {`stdout:\n${test.stdout}`}
            </pre>
          ) : null}
          {test.stderr ? (
            <pre className="mt-1 overflow-x-auto whitespace-pre-wrap text-xs text-ink-400">
              {`stderr:\n${test.stderr}`}
            </pre>
          ) : null}
        </div>
      )}
    </li>
  )
}

const RUN_ERROR = new Set(['timeout', 'error', 'collection_error'])

// Content of the bottom pane's "Unit Tests" tab. Leveled problems group by
// "Level N"; flat problems group by test-class name.
export default function TestResults({ results, canRun, levelCount }) {
  const tests = results?.tests ?? []
  const passed = tests.filter((t) => t.status === 'pass').length

  const groups = []
  for (let lvl = 1; lvl <= levelCount; lvl++) {
    const levelTests = tests.filter((t) => t.level === lvl)
    if (levelTests.length) {
      groups.push({ key: `lvl${lvl}`, label: `Level ${lvl}`, tests: levelTests })
    }
  }
  // Tests with no level (flat problems) are grouped by their class name.
  const flat = tests.filter((t) => !t.level)
  const classNames = []
  for (const t of flat) {
    if (!classNames.includes(t.class)) classNames.push(t.class)
  }
  for (const cls of classNames) {
    groups.push({
      key: cls,
      label: cls,
      tests: flat.filter((t) => t.class === cls),
    })
  }

  return (
    <div className="flex h-full flex-col">
      <div className="shrink-0 border-b border-ink-700 px-3 py-1.5 text-xs">
        {results && tests.length > 0 ? (
          <span className="text-ink-300">
            <b className="text-ink-100">
              {passed}/{tests.length}
            </b>{' '}
            passing &middot; ran at {results.ranAt}
          </span>
        ) : !canRun ? (
          <span className="text-ink-400">Start a session to run tests.</span>
        ) : (
          <span className="text-ink-400">No tests run yet.</span>
        )}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {results && RUN_ERROR.has(results.status) && (
          <div className="m-3 rounded border border-red-900 bg-red-950/40 p-3 text-xs text-red-300">
            <div className="font-semibold uppercase tracking-wide">
              {results.status}
            </div>
            <div className="mt-1 whitespace-pre-wrap">{results.message}</div>
            {results.traceback && (
              <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-red-400/80">
                {results.traceback}
              </pre>
            )}
          </div>
        )}

        {groups.map((g) => (
          <div key={g.key}>
            <div className="flex items-center gap-2 bg-ink-800 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-ink-300">
              <span>{g.label}</span>
              <span className="font-normal normal-case text-ink-400">
                {g.tests.filter((t) => t.status === 'pass').length}/
                {g.tests.length}
              </span>
            </div>
            <ul>
              {g.tests.map((t) => (
                <TestRow key={t.id} test={t} />
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
