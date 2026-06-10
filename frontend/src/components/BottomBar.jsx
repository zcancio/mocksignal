import BackupsMenu from './BackupsMenu'

export default function BottomBar({
  activeLevel,
  levelCount,
  problemName,
  results,
  saving,
  dirty,
  canReset,
  onReset,
  onRestored,
}) {
  return (
    <footer className="flex items-center gap-3 border-t border-ink-700 bg-ink-950 px-4 py-1.5 text-xs text-ink-400">
      {levelCount > 0 && (
        <>
          <span className="font-medium text-ink-300">Level {activeLevel}</span>
          <span className="text-ink-700">|</span>
        </>
      )}
      <span>
        {results
          ? `Last run ${results.ranAt} (${results.durationMs} ms)`
          : 'No runs yet'}
      </span>
      <span className="ml-auto">
        {saving ? 'Saving…' : dirty ? 'Unsaved changes' : 'All changes saved'}
      </span>
      <BackupsMenu problemName={problemName} onRestored={onRestored} />
      <button
        onClick={onReset}
        disabled={!canReset}
        className="rounded border border-ink-700 px-2 py-0.5 text-ink-300 hover:bg-ink-800 hover:text-ink-100 disabled:opacity-40 disabled:hover:bg-transparent"
      >
        Reset solution to stub
      </button>
    </footer>
  )
}
