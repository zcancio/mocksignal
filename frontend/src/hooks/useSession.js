import { useReducer } from 'react'

// Single source of truth for a practice session. The user's solution.py on
// disk is the real source of truth for code; this just tracks UI/session
// state that has no on-disk representation.

export const initialState = {
  problems: [],          // [{name, title}]
  problemName: null,
  problem: null,         // {title, description, levels, levelCount}
  loading: false,

  activeLevel: 1,        // which level tab is shown
  unlockedThrough: 1,    // highest unlocked level (latches up, never re-locks)

  editorContent: '',     // live editor buffer
  savedContent: '',      // what is known to be on disk
  saving: false,

  results: null,         // last run result from the backend
  running: false,

  durationMin: 90,
  session: 'idle',       // idle | running | ended
  sessionStartMs: null,

  editorReloadKey: 0,    // bumped to force a fresh editor (reset / restore)
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_PROBLEMS':
      return { ...state, problems: action.problems }

    case 'SET_DURATION':
      return { ...state, durationMin: action.minutes }

    case 'LOAD_START':
      return { ...state, loading: true }

    case 'LOAD_PROBLEM':
      return {
        ...state,
        loading: false,
        problemName: action.name,
        problem: action.problem,
        editorContent: action.content,
        savedContent: action.content,
        activeLevel: 1,
        unlockedThrough: 1,
        results: null,
        session: 'idle',
        sessionStartMs: null,
      }

    case 'SET_ACTIVE_LEVEL':
      return { ...state, activeLevel: action.level }

    case 'EDIT':
      return { ...state, editorContent: action.content }

    case 'SAVING':
      return { ...state, saving: true }

    case 'SAVED':
      return { ...state, saving: false, savedContent: action.content }

    case 'RUN_START':
      return { ...state, running: true }

    case 'RUN_DONE':
      return {
        ...state,
        running: false,
        results: action.results,
        // Unlocked levels latch — a later regression never re-locks them.
        unlockedThrough: Math.max(state.unlockedThrough, action.reached),
      }

    case 'RESET_DONE':
      return {
        ...state,
        editorContent: action.content,
        savedContent: action.content,
        editorReloadKey: state.editorReloadKey + 1,
      }

    case 'START_SESSION':
      return {
        ...state,
        session: 'running',
        sessionStartMs: Date.now(),
        results: null,
        unlockedThrough: 1,
        activeLevel: 1,
      }

    case 'END_SESSION':
      return { ...state, session: 'ended' }

    default:
      return state
  }
}

export function useSession() {
  return useReducer(reducer, initialState)
}
