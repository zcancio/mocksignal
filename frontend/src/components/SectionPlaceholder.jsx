// Shown when a non-"Desc" sidebar section is selected. Those sections exist
// for layout fidelity with CodeSignal but are intentionally not implemented.

const LABELS = {
  history: 'History',
  rules: 'Rules',
  readme: 'Readme',
  admin: 'Admin',
  settings: 'Settings',
}

export default function SectionPlaceholder({ section }) {
  return (
    <aside className="flex h-full w-full flex-col items-center justify-center gap-3 bg-ink-850 p-8 text-center">
      <div className="grid h-12 w-12 place-items-center rounded-full bg-ink-800 text-xl">
        {'\u{1F6A7}'}
      </div>
      <h3 className="text-sm font-semibold uppercase tracking-wider text-ink-300">
        {LABELS[section] ?? section}
      </h3>
      <p className="max-w-[15rem] text-xs leading-relaxed text-ink-400">
        This panel is part of the CodeSignal layout but isn&rsquo;t wired up in
        MockSignal. Switch back to{' '}
        <span className="font-semibold text-ink-300">Desc</span> for the problem
        statement and level tabs.
      </p>
    </aside>
  )
}
