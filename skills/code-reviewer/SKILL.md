---
name: code-reviewer
description: Review a code change and report findings prioritized as Critical, Warning, or Suggestion. Use when asked to review a diff, a pull request, or a file for correctness, security, tests, and readability before merging, or when self-checking your own changes before handing them off.
license: Apache-2.0
---

# Code Reviewer

A checklist and output format for reviewing code changes.

## When to use

Use when reviewing a diff, PR, or file, or when finishing an implementation and
you want a structured self-check before handing work off.

## Workflow

1. **Understand the intent.** What is this change supposed to do?
2. **Walk the diff** against `references/checklist.md` across five lenses:
   correctness, security, tests, readability, and performance.
3. **For each issue,** assign a severity and write a concrete, actionable fix
   with a `file:line` reference and the reason it matters.
4. **Report** findings grouped by severity, most severe first.

## Output format

```markdown
### Critical (must fix before merge)
- `path:line`: <problem>. Fix: <action>.

### Warning (should fix)
- `path:line`: <problem>. Fix: <action>.

### Suggestion (nice to have)
- `path:line`: <improvement>.
```

If a category has no findings, write `None`.

## Guidelines

- Be specific and reproducible: cite `file:line` and explain the reasoning.
- Prioritize correctness and security over style; don't bury real issues under
  nitpicks.
- See `references/checklist.md` for the full, category-by-category checklist.
