import { useEffect, useRef } from 'react'
import { Terminal as XTerm } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'

const THEME = {
  background: '#141a2e',
  foreground: '#c5cbd9',
  cursor: '#4d82ff',
  cursorAccent: '#141a2e',
  selectionBackground: '#2f3e6b',
  black: '#0d1120',
  red: '#f87171',
  green: '#34d399',
  yellow: '#fbbf24',
  blue: '#60a5fa',
  magenta: '#c084fc',
  cyan: '#22d3ee',
  white: '#c5cbd9',
  brightBlack: '#46506f',
  brightRed: '#fca5a5',
  brightGreen: '#6ee7b7',
  brightYellow: '#fcd34d',
  brightBlue: '#93c5fd',
  brightMagenta: '#d8b4fe',
  brightCyan: '#67e8f9',
  brightWhite: '#e7e9f1',
}

// A real PTY-backed terminal (xterm.js <-> backend WebSocket). The shell is
// rooted in the problem directory, so `python -m pdb tests.py` just works.
export default function Terminal({ problemName, active, resizeKey }) {
  const hostRef = useRef(null)
  const termRef = useRef(null)
  const fitRef = useRef(null)
  const wsRef = useRef(null)

  useEffect(() => {
    if (!problemName) return undefined

    const term = new XTerm({
      fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
      fontSize: 12.5,
      theme: THEME,
      cursorBlink: true,
      scrollback: 5000,
    })
    const fit = new FitAddon()
    term.loadAddon(fit)
    term.open(hostRef.current)
    termRef.current = term
    fitRef.current = fit
    try {
      fit.fit()
    } catch {
      /* container not sized yet */
    }

    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(
      `${proto}://${location.host}/api/problems/${problemName}/terminal`,
    )
    ws.binaryType = 'arraybuffer'
    wsRef.current = ws

    const sendResize = () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }),
        )
      }
    }
    ws.onopen = () => {
      try {
        fit.fit()
      } catch {
        /* ignore */
      }
      sendResize()
      term.focus()
    }
    ws.onmessage = (e) => term.write(new Uint8Array(e.data))
    ws.onclose = () =>
      term.write('\r\n\x1b[2m[ terminal session ended ]\x1b[0m\r\n')

    const dataSub = term.onData((d) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'input', data: d }))
      }
    })
    const onWinResize = () => {
      try {
        fit.fit()
      } catch {
        /* ignore */
      }
      sendResize()
    }
    window.addEventListener('resize', onWinResize)

    return () => {
      window.removeEventListener('resize', onWinResize)
      dataSub.dispose()
      try {
        ws.close()
      } catch {
        /* ignore */
      }
      term.dispose()
      termRef.current = null
      fitRef.current = null
      wsRef.current = null
    }
  }, [problemName])

  // Re-fit whenever the pane is shown or resized (the divider drag, tab switch).
  useEffect(() => {
    if (!active) return undefined
    const id = setTimeout(() => {
      const fit = fitRef.current
      const term = termRef.current
      const ws = wsRef.current
      if (!fit || !term) return
      try {
        fit.fit()
      } catch {
        /* ignore */
      }
      term.focus()
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }),
        )
      }
    }, 40)
    return () => clearTimeout(id)
  }, [active, resizeKey])

  return <div ref={hostRef} className="h-full w-full px-2 pt-1" />
}
