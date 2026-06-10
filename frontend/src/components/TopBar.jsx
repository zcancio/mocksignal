import Timer from './Timer'

export default function TopBar({
  problems,
  problemName,
  onSelectProblem,
  session,
  sessionStartMs,
  durationMin,
  onStart,
  onEnd,
  onExpire,
}) {
  return (
    <header className="flex items-center gap-3 border-b border-ink-700 bg-ink-950 px-4 py-2">
      <div className="flex items-center gap-2">
        <span className="grid h-6 w-6 place-items-center rounded bg-accent text-sm font-bold text-white">
          M
        </span>
        <span className="font-semibold tracking-tight text-ink-100">MockSignal</span>
      </div>

      <div className="mx-1 h-5 w-px bg-ink-700" />

      <span className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
        Problem
      </span>
      <select
        className="rounded border border-ink-700 bg-ink-800 px-2 py-1 text-sm text-ink-100 outline-none hover:border-ink-600 disabled:opacity-50"
        value={problemName ?? ''}
        disabled={session === 'running'}
        onChange={(e) => onSelectProblem(e.target.value)}
      >
        {problems.length === 0 && <option value="">No problems found</option>}
        {problems.map((p) => (
          <option key={p.name} value={p.name}>
            {p.title}
          </option>
        ))}
      </select>

      <div className="ml-auto flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
            Time
          </span>
          <Timer
            session={session}
            startMs={sessionStartMs}
            durationMin={durationMin}
            onExpire={onExpire}
          />
        </div>
        {session === 'running' ? (
          <button
            onClick={onEnd}
            className="rounded bg-ink-700 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-ink-100 hover:bg-ink-600"
          >
            End session
          </button>
        ) : (
          <button
            onClick={onStart}
            disabled={!problemName}
            className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-white hover:bg-emerald-500 disabled:opacity-50"
          >
            Start session
          </button>
        )}
      </div>
    </header>
  )
}
