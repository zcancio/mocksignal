import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Mio-style copilot chat. Lives in the left rail; talks to /api/copilot,
// which streams a Claude reply with the workspace + open files + terminal as
// context.

// Flatten a markdown AST node to its raw text (for the copy button).
function nodeText(node) {
  if (!node) return ''
  if (typeof node.value === 'string') return node.value
  return (node.children || []).map(nodeText).join('')
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text)
    } catch {
      // Fallback for non-secure contexts.
      const ta = document.createElement('textarea')
      ta.value = text
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.select()
      try {
        document.execCommand('copy')
      } catch {
        /* give up silently */
      }
      document.body.removeChild(ta)
    }
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  return (
    <button
      onClick={copy}
      className="absolute right-1.5 top-1.5 rounded border border-ink-700 bg-ink-850/90 px-2 py-0.5 text-[11px] font-medium text-ink-300 opacity-0 transition-opacity hover:border-accent hover:text-white group-hover:opacity-100"
    >
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

// Render fenced code blocks with a hover copy button.
function Pre({ node, children }) {
  return (
    <div className="group relative">
      <CopyButton text={nodeText(node)} />
      <pre>{children}</pre>
    </div>
  )
}

function Markdown({ children }) {
  return (
    <div className="markdown text-[13px] leading-relaxed">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ pre: Pre }}>
        {children}
      </ReactMarkdown>
    </div>
  )
}

const SUGGESTIONS = [
  'Give me a hint for the current level',
  'Explain what this problem is asking',
  'Why are my tests failing?',
  'Review my current code',
]

function Bubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={isUser ? 'flex justify-end' : 'flex justify-start'}>
      <div
        className={[
          'max-w-[92%] rounded-lg px-3 py-2',
          isUser
            ? 'bg-accent text-white'
            : 'bg-ink-800 text-ink-100',
        ].join(' ')}
      >
        {isUser ? (
          <div className="whitespace-pre-wrap text-[13px] leading-relaxed">
            {message.content}
          </div>
        ) : message.content ? (
          <Markdown>{message.content}</Markdown>
        ) : message.error ? null : (
          <span className="inline-flex gap-1 py-1 text-ink-400">
            <Dot /> <Dot delay="0.15s" /> <Dot delay="0.3s" />
          </span>
        )}
        {message.error && (
          <div className="mt-1 text-[12px] text-red-300">{message.error}</div>
        )}
      </div>
    </div>
  )
}

function Dot({ delay = '0s' }) {
  return (
    <span
      className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-ink-400"
      style={{ animationDelay: delay }}
    />
  )
}

export default function CopilotPanel({
  messages,
  sending,
  ready,
  onSend,
  onCancel,
  onClear,
}) {
  const [text, setText] = useState('')
  const scrollRef = useRef(null)
  const taRef = useRef(null)

  // Stick to the bottom as new content streams in.
  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [messages])

  // Grow the textarea with its content, up to the max-height cap.
  const autoGrow = () => {
    const el = taRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
  }
  useEffect(autoGrow, [text])

  const submit = () => {
    const t = text.trim()
    if (!t || sending) return
    onSend(t)
    setText('')
  }

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <aside className="flex h-full w-full flex-col bg-ink-850">
      <div className="flex items-center justify-between border-b border-ink-700 px-4 py-3">
        <div>
          <div className="text-[11px] font-medium uppercase tracking-wider text-ink-400">
            Copilot
          </div>
          <h2 className="mt-0.5 text-base font-semibold text-ink-100">Mio</h2>
        </div>
        {messages.length > 0 && (
          <button
            onClick={onClear}
            className="rounded px-2 py-1 text-xs text-ink-400 hover:bg-ink-800 hover:text-ink-200"
          >
            New chat
          </button>
        )}
      </div>

      <div
        ref={scrollRef}
        className="min-h-0 flex-1 space-y-3 overflow-y-auto px-3 py-3"
      >
        {messages.length === 0 ? (
          <div className="px-1 py-2 text-sm text-ink-400">
            <p className="text-ink-300">
              Hi, I&rsquo;m Mio — your coding copilot.
            </p>
            <p className="mt-1.5 leading-relaxed">
              I can see the problem, every <strong>open file</strong>, the
              workspace file list, and your <strong>terminal</strong> history.
              If I need a file you haven&rsquo;t opened, I&rsquo;ll ask you to
              open it. Code I write has a <strong>Copy</strong> button.
            </p>
            <div className="mt-3 flex flex-col gap-1.5">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  disabled={!ready}
                  onClick={() => onSend(s)}
                  className="rounded-md border border-ink-700 bg-ink-900 px-3 py-2 text-left text-[13px] text-ink-200 transition-colors hover:border-accent hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, i) => <Bubble key={i} message={m} />)
        )}
      </div>

      <div className="border-t border-ink-700 p-2.5">
        <div className="flex items-end gap-2 rounded-lg border border-ink-700 bg-ink-900 px-2.5 py-2 focus-within:border-accent">
          <textarea
            ref={taRef}
            rows={1}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder={ready ? 'Ask Mio…' : 'Load a problem to start'}
            disabled={!ready}
            className="max-h-32 min-h-[20px] flex-1 resize-none bg-transparent text-[13px] text-ink-100 placeholder:text-ink-400 focus:outline-none disabled:cursor-not-allowed"
          />
          {sending ? (
            <button
              onClick={onCancel}
              title="Stop"
              className="grid h-7 w-7 shrink-0 place-items-center rounded-md bg-ink-700 text-ink-100 hover:bg-ink-600"
            >
              <span className="h-2.5 w-2.5 rounded-[2px] bg-current" />
            </button>
          ) : (
            <button
              onClick={submit}
              disabled={!ready || !text.trim()}
              title="Send"
              className="grid h-7 w-7 shrink-0 place-items-center rounded-md bg-accent text-white hover:bg-accent-bright disabled:cursor-not-allowed disabled:opacity-40"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                <path d="M12 19V5M5 12l7-7 7 7" />
              </svg>
            </button>
          )}
        </div>
        <p className="mt-1 px-1 text-[10px] text-ink-400">
          Mio can make mistakes. Enter to send, Shift+Enter for a newline.
        </p>
      </div>
    </aside>
  )
}
