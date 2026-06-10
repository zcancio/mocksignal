import { useEffect, useRef, useState } from 'react'

function fmt(ms) {
  const total = Math.floor(Math.max(0, ms) / 1000)
  const m = String(Math.floor(total / 60)).padStart(2, '0')
  const s = String(total % 60).padStart(2, '0')
  return `${m}:${s}`
}

// Countdown derived purely from a fixed start timestamp + duration. There is
// no pause: once a session starts, the clock runs no matter what.
export default function Timer({ session, startMs, durationMin, onExpire }) {
  const [now, setNow] = useState(() => Date.now())
  const expired = useRef(false)

  useEffect(() => {
    if (session !== 'running') return
    expired.current = false
    setNow(Date.now())
    const id = setInterval(() => setNow(Date.now()), 500)
    return () => clearInterval(id)
  }, [session, startMs])

  const totalMs = durationMin * 60000
  const remaining = startMs ? startMs + totalMs - now : totalMs

  useEffect(() => {
    if (session === 'running' && remaining <= 0 && !expired.current) {
      expired.current = true
      onExpire()
    }
  }, [remaining, session, onExpire])

  let color = 'text-ink-400'
  if (session === 'running') {
    if (remaining <= 5 * 60000) color = 'text-red-400'
    else if (remaining <= 15 * 60000) color = 'text-yellow-400'
    else color = 'text-emerald-400'
  }

  return (
    <span className={`font-mono text-base font-semibold tabular-nums ${color}`}>
      {fmt(remaining)}
    </span>
  )
}
