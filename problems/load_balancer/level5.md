## Level 5 — Scale

Same external API. Now the test runs with **10,000 servers and 100,000
requests**. The naive O(S) per-route implementation that passed L1
will time out.

You'll need to refactor `route` (and probably `top_servers`) to be
faster. The standard library has the tools you need (`heapq`,
`bisect`). You should NOT need third-party libraries.
