// Shown when a session ends. Score is "X of Y", broken down by level —
// deliberately not a percentage, matching how CodeSignal scores at a glance.
export default function ScoreModal({ score, problemTitle, onClose }) {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-ink-950/80">
      <div className="w-80 rounded-lg border border-ink-700 bg-ink-850 p-5 shadow-2xl">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-ink-400">
          Session ended
        </h2>
        <p className="mt-0.5 text-sm text-ink-300">{problemTitle}</p>

        <div className="mt-4 text-ink-100">
          <span className="text-3xl font-bold">{score.pass}</span>
          <span className="mx-1 text-ink-400">of</span>
          <span className="text-3xl font-bold">{score.total}</span>
          <span className="ml-2 text-sm text-ink-400">tests passing</span>
        </div>

        <ul className="mt-4 space-y-1 text-sm">
          {Object.entries(score.byLevel).map(([lvl, s]) => (
            <li
              key={lvl}
              className="flex justify-between border-b border-ink-700/50 pb-1"
            >
              <span className="text-ink-300">Level {lvl}</span>
              <span
                className={
                  s.total > 0 && s.pass === s.total
                    ? 'font-medium text-emerald-400'
                    : 'text-ink-100'
                }
              >
                {s.pass} / {s.total}
              </span>
            </li>
          ))}
        </ul>

        <button
          onClick={onClose}
          className="mt-5 w-full rounded bg-accent py-2 text-sm font-semibold text-white hover:bg-accent-bright"
        >
          Close
        </button>
      </div>
    </div>
  )
}
