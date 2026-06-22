// Left icon rail, styled after the CodeSignal IDE. Only "Desc" is wired up;
// the rest are present for layout fidelity and show a placeholder panel.

function Svg({ children }) {
  return (
    <svg
      width="21"
      height="21"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      {children}
    </svg>
  )
}

const ICONS = {
  copilot: (
    <Svg>
      <path d="M12 3a3 3 0 0 1 3 3v1h1a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-6a3 3 0 0 1 3-3h1V6a3 3 0 0 1 3-3z" />
      <path d="M9.5 13v1.5M14.5 13v1.5" />
      <path d="M12 3V1.5" />
    </Svg>
  ),
  desc: (
    <Svg>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5" />
      <path d="M9 13h6M9 17h6" />
    </Svg>
  ),
  history: (
    <Svg>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </Svg>
  ),
  rules: (
    <Svg>
      <rect x="6" y="4" width="12" height="16" rx="2" />
      <rect x="9" y="2.5" width="6" height="3" rx="1" />
      <path d="M9.5 10h5M9.5 14h5" />
    </Svg>
  ),
  readme: (
    <Svg>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 11v5" />
      <path d="M12 8h.01" />
    </Svg>
  ),
  admin: (
    <Svg>
      <path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z" />
      <path d="M9 12l2 2 4-4" />
    </Svg>
  ),
  settings: (
    <Svg>
      <path d="M4 7.5h9M17 7.5h3" />
      <circle cx="15" cy="7.5" r="2" />
      <path d="M4 16.5h3M11 16.5h9" />
      <circle cx="9" cy="16.5" r="2" />
    </Svg>
  ),
}

const SECTIONS = [
  { id: 'copilot', label: 'Copilot' },
  { id: 'desc', label: 'Desc' },
  { id: 'history', label: 'History' },
  { id: 'rules', label: 'Rules' },
  { id: 'readme', label: 'Readme' },
  { id: 'admin', label: 'Admin' },
  { id: 'settings', label: 'Settings' },
]

export default function Sidebar({ active, onSelect }) {
  return (
    <nav className="flex w-16 shrink-0 flex-col border-r border-ink-700 bg-ink-950 py-1">
      {SECTIONS.map((s) => {
        const isActive = s.id === active
        return (
          <button
            key={s.id}
            onClick={() => onSelect(s.id)}
            className={[
              'flex flex-col items-center gap-1 py-2.5 transition-colors',
              isActive
                ? 'bg-accent text-white'
                : 'text-ink-400 hover:bg-ink-800 hover:text-ink-200',
            ].join(' ')}
          >
            {ICONS[s.id]}
            <span className="text-[9px] font-semibold uppercase tracking-wide">
              {s.label}
            </span>
          </button>
        )
      })}
    </nav>
  )
}
