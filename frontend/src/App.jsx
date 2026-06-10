import { useCallback, useEffect, useRef, useState } from 'react'
import { useSession } from './hooks/useSession'
import { api } from './lib/api'
import { reachedLevel, computeScore } from './lib/grading'
import TopBar from './components/TopBar'
import Sidebar from './components/Sidebar'
import ProblemPanel from './components/ProblemPanel'
import SectionPlaceholder from './components/SectionPlaceholder'
import FilesPanel from './components/FilesPanel'
import EditorPane from './components/EditorPane'
import BottomPane from './components/BottomPane'
import BottomBar from './components/BottomBar'
import ScoreModal from './components/ScoreModal'

const SAVE_DEBOUNCE_MS = 800

export default function App() {
  const [state, dispatch] = useSession()
  const saveTimer = useRef(null)

  const [activeSection, setActiveSection] = useState('desc')

  // Resizable pane sizes (px).
  const [descWidth, setDescWidth] = useState(340)
  const [filesWidth, setFilesWidth] = useState(208)
  const [bottomHeight, setBottomHeight] = useState(264)

  // Open editor files / tabs. solution.py is always open; read-only files
  // (tests.py) are fetched on demand and cached.
  const [filesList, setFilesList] = useState([])
  const [openFiles, setOpenFiles] = useState([
    { name: 'solution.py', editable: true },
  ])
  const [activeFile, setActiveFile] = useState('solution.py')
  const [fileCache, setFileCache] = useState({})

  const loadProblem = useCallback(
    async (name) => {
      dispatch({ type: 'LOAD_START' })
      const [problem, sol, files] = await Promise.all([
        api.getProblem(name),
        api.getSolution(name),
        api.listFiles(name),
      ])
      dispatch({ type: 'LOAD_PROBLEM', name, problem, content: sol.content })
      setFilesList(files)
      setFileCache({})
      setOpenFiles([{ name: 'solution.py', editable: true }])
      setActiveFile('solution.py')
    },
    [dispatch],
  )

  // Initial load: timer config, problem list, then the first problem.
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [cfg, problems] = await Promise.all([
          api.config(),
          api.listProblems(),
        ])
        if (cancelled) return
        dispatch({ type: 'SET_DURATION', minutes: cfg.defaultTimerMinutes })
        dispatch({ type: 'SET_PROBLEMS', problems })
        if (problems.length) await loadProblem(problems[0].name)
      } catch (e) {
        console.error('Failed to load — is the backend running on :8000?', e)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [dispatch, loadProblem])

  // Immediately persist the solution buffer — used by the debounce and ⌘S.
  const saveNow = useCallback(async () => {
    if (state.editorContent === state.savedContent) return
    if (saveTimer.current) {
      clearTimeout(saveTimer.current)
      saveTimer.current = null
    }
    const content = state.editorContent
    dispatch({ type: 'SAVING' })
    try {
      await api.saveSolution(state.problemName, content)
      dispatch({ type: 'SAVED', content })
    } catch (e) {
      console.error('Save failed', e)
    }
  }, [state.editorContent, state.savedContent, state.problemName, dispatch])

  // Debounced auto-save while a session is running.
  useEffect(() => {
    if (state.session !== 'running') return undefined
    if (state.editorContent === state.savedContent) return undefined
    if (saveTimer.current) clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(saveNow, SAVE_DEBOUNCE_MS)
    return () => saveTimer.current && clearTimeout(saveTimer.current)
  }, [state.editorContent, state.savedContent, state.session, saveNow])

  // Latest-saveNow ref, so the key listener can subscribe just once.
  const saveNowRef = useRef(saveNow)
  saveNowRef.current = saveNow

  // ⌘S / Ctrl+S saves immediately (on top of auto-save).
  useEffect(() => {
    const onKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && (e.key === 's' || e.key === 'S')) {
        e.preventDefault()
        saveNowRef.current()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  const runTests = useCallback(async () => {
    dispatch({ type: 'RUN_START' })
    try {
      // Flush any pending edits so tests run against the current file.
      if (state.editorContent !== state.savedContent) {
        await api.saveSolution(state.problemName, state.editorContent)
        dispatch({ type: 'SAVED', content: state.editorContent })
      }
      const results = await api.runTests(state.problemName)
      const reached = reachedLevel(state.problem?.levelCount ?? 0, results)
      dispatch({ type: 'RUN_DONE', results, reached })
    } catch (e) {
      dispatch({
        type: 'RUN_DONE',
        results: { status: 'error', message: String(e), tests: [] },
        reached: 1,
      })
    }
  }, [
    state.editorContent,
    state.savedContent,
    state.problemName,
    state.problem,
    dispatch,
  ])

  const resetSolution = useCallback(async () => {
    const ok = window.confirm(
      'Reset solution to the stub?\n\nThis permanently discards your current work.',
    )
    if (!ok) return
    const { content } = await api.reset(state.problemName)
    dispatch({ type: 'RESET_DONE', content })
  }, [state.problemName, dispatch])

  // Open a file from the navigator as an editor tab (fetching it if read-only).
  const openFile = useCallback(
    async (name) => {
      const meta =
        filesList.find((f) => f.name === name) ??
        { name, editable: name === 'solution.py' }
      if (!meta.editable && fileCache[name] === undefined) {
        try {
          const { content } = await api.getFile(state.problemName, name)
          setFileCache((c) => ({ ...c, [name]: content }))
        } catch (e) {
          console.error('Could not open file', name, e)
          return
        }
      }
      setOpenFiles((f) => (f.some((x) => x.name === name) ? f : [...f, meta]))
      setActiveFile(name)
    },
    [filesList, fileCache, state.problemName],
  )

  const closeFile = useCallback((name) => {
    if (name === 'solution.py') return
    setOpenFiles((f) => f.filter((x) => x.name !== name))
    setActiveFile((a) => (a === name ? 'solution.py' : a))
  }, [])

  // Generic drag-to-resize for the pane separators.
  const beginResize = (e, opts) => {
    e.preventDefault()
    const { axis, value, setValue, min, max, invert } = opts
    const startPos = axis === 'x' ? e.clientX : e.clientY
    const onMove = (ev) => {
      const pos = axis === 'x' ? ev.clientX : ev.clientY
      const delta = (invert ? -1 : 1) * (pos - startPos)
      setValue(Math.max(min, Math.min(value + delta, max)))
    }
    const stop = () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', stop)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', stop)
    document.body.style.cursor = axis === 'x' ? 'col-resize' : 'row-resize'
    document.body.style.userSelect = 'none'
  }

  const VHandle = ({ value, setValue, min, max }) => (
    <div
      onMouseDown={(e) => beginResize(e, { axis: 'x', value, setValue, min, max })}
      className="w-1.5 shrink-0 cursor-col-resize bg-ink-900 hover:bg-accent"
    />
  )

  const score =
    state.session === 'ended'
      ? computeScore(state.problem?.levelCount ?? 0, state.results)
      : null
  const dirty = state.editorContent !== state.savedContent
  const sessionLocked = state.session !== 'running'
  const openFilesWithContent = openFiles.map((f) => ({
    ...f,
    content:
      f.name === 'solution.py' ? state.editorContent : fileCache[f.name] ?? '',
  }))

  return (
    <div className="relative flex h-full flex-col bg-ink-900 text-ink-100">
      <TopBar
        problems={state.problems}
        problemName={state.problemName}
        onSelectProblem={loadProblem}
        session={state.session}
        sessionStartMs={state.sessionStartMs}
        durationMin={state.durationMin}
        onStart={() => dispatch({ type: 'START_SESSION' })}
        onEnd={() => dispatch({ type: 'END_SESSION' })}
        onExpire={() => dispatch({ type: 'END_SESSION' })}
      />

      <div className="flex min-h-0 flex-1">
        <Sidebar active={activeSection} onSelect={setActiveSection} />

        <div className="shrink-0" style={{ width: descWidth }}>
          {activeSection === 'desc' ? (
            <ProblemPanel
              problem={state.problem}
              activeLevel={state.activeLevel}
              unlockedThrough={state.unlockedThrough}
              onSelectLevel={(level) =>
                dispatch({ type: 'SET_ACTIVE_LEVEL', level })
              }
            />
          ) : (
            <SectionPlaceholder section={activeSection} />
          )}
        </div>
        <VHandle
          value={descWidth}
          setValue={setDescWidth}
          min={240}
          max={620}
        />

        <div className="flex min-w-0 flex-1 flex-col">
          <div className="flex min-h-0 flex-1">
            <div className="shrink-0" style={{ width: filesWidth }}>
              <FilesPanel
                files={filesList}
                activeFile={activeFile}
                onOpen={openFile}
              />
            </div>
            <VHandle
              value={filesWidth}
              setValue={setFilesWidth}
              min={150}
              max={420}
            />
            <EditorPane
              problemName={state.problemName}
              openFiles={openFilesWithContent}
              activeFile={activeFile}
              reloadKey={state.editorReloadKey}
              sessionLocked={sessionLocked}
              saving={state.saving}
              dirty={dirty}
              onSelectFile={setActiveFile}
              onCloseFile={closeFile}
              onChange={(c) => dispatch({ type: 'EDIT', content: c })}
            />
          </div>

          <div
            onMouseDown={(e) =>
              beginResize(e, {
                axis: 'y',
                value: bottomHeight,
                setValue: setBottomHeight,
                min: 120,
                max: window.innerHeight - 220,
                invert: true,
              })
            }
            className="h-1.5 shrink-0 cursor-row-resize bg-ink-900 hover:bg-accent"
          />

          <div className="shrink-0" style={{ height: bottomHeight }}>
            <BottomPane
              key={state.problemName ?? 'none'}
              problemName={state.problemName}
              results={state.results}
              running={state.running}
              canRun={state.session === 'running'}
              levelCount={state.problem?.levelCount ?? 0}
              onRun={runTests}
              resizeKey={bottomHeight}
            />
          </div>
        </div>
      </div>

      <BottomBar
        activeLevel={state.activeLevel}
        levelCount={state.problem?.levelCount ?? 0}
        problemName={state.problemName}
        results={state.results}
        saving={state.saving}
        dirty={dirty}
        canReset={state.session === 'running'}
        onReset={resetSolution}
        onRestored={(content) => dispatch({ type: 'RESET_DONE', content })}
      />

      {score && (
        <ScoreModal
          score={score}
          problemTitle={state.problem?.title}
          onClose={() => loadProblem(state.problemName)}
        />
      )}
    </div>
  )
}
