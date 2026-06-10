// Small shared icons for file tabs and the file navigator.

// A blue/yellow chip evoking the Python file icon.
export function PyChip() {
  return (
    <span className="flex h-3.5 w-3.5 shrink-0 overflow-hidden rounded-[3px]">
      <span className="w-1/2 bg-[#3b72b0]" />
      <span className="w-1/2 bg-[#ffd23f]" />
    </span>
  )
}

export function LockIcon({ className = '' }) {
  return (
    <svg
      width="11"
      height="11"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`shrink-0 ${className}`}
      aria-hidden
    >
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V8a4 4 0 0 1 8 0v3" />
    </svg>
  )
}

export function CloseIcon() {
  return (
    <svg
      width="11"
      height="11"
      viewBox="0 0 12 12"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      aria-hidden
    >
      <path d="M3 3l6 6M9 3l-6 6" />
    </svg>
  )
}
