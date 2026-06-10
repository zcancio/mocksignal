import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function Markdown({ children }) {
  return (
    <div className="markdown text-sm leading-relaxed">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  )
}

// Left pane: problem overview + level tabs. Every level's description is
// readable from the start (matches real CodeSignal ICF — read all levels,
// then design, then code). Progress is signalled by per-level pass tallies
// in the test pane and score modal, not by hiding content.
//
// A "flat" problem (no levelN.md files) shows just its description.
export default function ProblemPanel({
  problem,
  activeLevel,
  onSelectLevel,
}) {
  if (!problem) {
    return (
      <aside className="h-full w-full bg-ink-850 p-4 text-sm text-ink-400">
        Loading…
      </aside>
    )
  }

  if (problem.levels.length === 0) {
    return (
      <aside className="flex h-full w-full flex-col bg-ink-850">
        <div className="border-b border-ink-700 px-4 py-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
            Description
          </div>
          <h2 className="mt-1 text-base font-semibold text-ink-100">
            {problem.title}
          </h2>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3">
          <Markdown>{problem.description}</Markdown>
        </div>
      </aside>
    )
  }

  const active = problem.levels.find((l) => l.level === activeLevel)

  return (
    <aside className="flex h-full w-full flex-col bg-ink-850">
      <div className="border-b border-ink-700 px-4 py-3">
        <div className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
          Description
        </div>
        <h2 className="mt-1 text-base font-semibold text-ink-100">
          {problem.title}
        </h2>
        <div className="mt-1 max-h-44 overflow-y-auto pr-1">
          <Markdown>{problem.description}</Markdown>
        </div>
      </div>

      <div className="flex gap-0.5 border-b border-ink-700 bg-ink-900 px-2 pt-2">
        {problem.levels.map((l) => {
          const isActive = l.level === activeLevel
          return (
            <button
              key={l.level}
              onClick={() => onSelectLevel(l.level)}
              className={[
                'rounded-t border-t-2 px-3 py-1.5 text-xs font-medium transition-colors',
                isActive
                  ? 'border-accent bg-ink-850 text-ink-100'
                  : 'border-transparent text-ink-400 hover:text-ink-300',
              ].join(' ')}
            >
              Level {l.level}
            </button>
          )
        })}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3">
        <Markdown>{active?.markdown ?? ''}</Markdown>
      </div>
    </aside>
  )
}
