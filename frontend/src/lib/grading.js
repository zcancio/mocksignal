// Pure helpers for level gating and scoring, derived from a test result set.

// How far has the solver progressed? Returns the highest level number that
// should be accessible: level N unlocks only once every test in level N-1
// has passed. Progression stops at the first level that is not fully green.
export function reachedLevel(levelCount, results) {
  let reached = 1
  if (!results || !results.tests) return reached
  for (let lvl = 1; lvl < levelCount; lvl++) {
    const tests = results.tests.filter((t) => t.level === lvl)
    const allPass = tests.length > 0 && tests.every((t) => t.status === 'pass')
    if (allPass) reached = lvl + 1
    else break
  }
  return reached
}

// "X of Y" breakdown — overall and per level — for the end-of-session score.
export function computeScore(levelCount, results) {
  if (!results || !results.tests) return null
  const byLevel = {}
  for (let l = 1; l <= levelCount; l++) byLevel[l] = { pass: 0, total: 0 }
  let pass = 0
  for (const t of results.tests) {
    if (t.status === 'pass') pass += 1
    if (t.level && byLevel[t.level]) {
      byLevel[t.level].total += 1
      if (t.status === 'pass') byLevel[t.level].pass += 1
    }
  }
  return { pass, total: results.tests.length, byLevel }
}
