# Code review checklist

The full checklist, loaded on demand. Map each item to a severity
(Critical / Warning / Suggestion) when you report.

## Correctness
- Does the code do what the change description claims?
- Are edge cases handled (empty input, nulls, large input, unicode, timezones)?
- Off-by-one, boundary, and integer/float pitfalls?
- Error handling: are failures caught at the right level and surfaced, not swallowed?
- Concurrency: shared state, races, ordering assumptions?

## Security
- Untrusted input validated/sanitized before use (paths, SQL, shell, HTML)?
- No secrets, keys, or tokens committed; secrets read from the environment?
- No `eval`/`exec`/shell-injection or unsafe deserialization of untrusted data?
- Network calls: expected, authenticated, and least-privilege?
- Dependencies: pinned and from trusted sources?

## Tests
- Are new code paths covered by tests?
- Do tests assert behavior (not just "it runs")? Are assertions meaningful?
- Are failure modes and edge cases tested, not only the happy path?
- Are tests deterministic (no reliance on time, network, or ordering)?

## Readability & maintainability
- Clear names; functions do one thing; reasonable size?
- Comments explain *why*, not *what*; no dead/commented-out code?
- Consistent with surrounding style and conventions?
- Public functions documented with a usage example?

## Performance
- Any obvious O(n^2)+ hot paths or needless work in loops?
- Unbounded memory growth or resource leaks (files/sockets not closed)?
- Repeated expensive calls that could be hoisted or cached?

## Output severities
- **Critical** — bugs, security holes, data loss, broken builds. Must fix.
- **Warning** — likely problems, missing tests, fragile code. Should fix.
- **Suggestion** — style, naming, minor cleanups. Nice to have.
