---
name: findings
description: What to do when stress testing finds a bug — GitHub issues by default, artifacts when needed, auto-fix only when asked.
---

# Findings: What To Do With Bugs

Shared policy for comb, mischief, and bug hunter. Modes decide *how* to hunt; this file decides *what happens when you catch something*.

## Defaults

| Situation | Do this |
|-----------|---------|
| Repo has GitHub and you can file issues | **One issue per distinct real finding**; give the user hyperlinks when you summarize |
| No GitHub / no permission | Write a **markdown or HTML artifact** (preferably in-repo so it can be committed) |
| User asked to auto-fix | Fix **small, additive, tested** knots as you go; still **file** large or load-bearing ones |
| Unclear | Ask once, then proceed with filing |

**GitHub smoke test:** before a batch of real issues, create a throwaway issue and delete it to prove permissions.

## What counts as a "real" finding

Do **not** file from a single flaky signal. Cross-check before filing:

1. UI / agent-browser observation (if relevant)
2. Console / network
3. API or backend truth
4. Infra/deploy state when symptoms look like 502, blank page, or stale chunks

A scary screenshot is not a bug until another layer agrees. A clean screenshot is not proof the backend is healthy.

Rule out false alarms: deploy/roll in flight, stale SPA, your own earlier mutations, tool limitations. See [driving.md](driving.md).

## Issue / artifact quality

Each finding should include:

- **Title** that names the failure, not the session ("Submit double-posts order" not "mischief pass 3")
- **Repro** — UI steps *or* API sequence (no secrets)
- **Expected vs actual**
- **Evidence** — status codes, response snippets, console errors, screenshots if useful
- **Surface** — browser, API, or both (especially when they disagree)
- **Severity guess** — user-blocking / data-corrupting / cosmetic / latent

One distinct bug per issue. Don't dump a whole session into a single ticket.

## After the pass

Summarize for the user: what you ran (comb / mischief / bug hunter), surfaces used (browser / API), links to issues or path to the artifact, and ask which items to fix now if they haven't already said.

## See also

- [driving.md](driving.md) · [comb.md](comb.md) · [mischief.md](mischief.md) · [bug-hunter.md](bug-hunter.md)
