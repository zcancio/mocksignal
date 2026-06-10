# Speed 1 — Word Count

_Speed warmup &middot; target: under 5 minutes._

Implement `word_count(text)` — return a dict mapping each word to its count.
Words are separated by whitespace; matching is case-insensitive.

```python
word_count("The quick brown fox the FOX")
# -> {"the": 2, "quick": 1, "brown": 1, "fox": 2}
```

Then implement `top_words(text, n)` — the `n` most common words as a list of
`(word, count)` tuples, sorted by count descending, then by word ascending
for ties.

_The test file is the spec — open `tests.py` from the Files panel for the
exact expected behaviour._
