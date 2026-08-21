---
name: comment-rules
description: How and when to comment on Linear issues. Be heavy on comments.
---

# Comment Rules
Issues are the durable record; conversations and terminal sessions evaporate. **Err heavily on the side of too many comments.** A future reader (the user, a teammate, or another agent picking the issue up cold) should be able to reconstruct the whole story of the issue from its comments alone, without asking anyone.

## When to comment (at minimum)
- **On create:** any context that didn't fit the description — links, screenshots, the conversation that spawned it.
- **On start:** that work is starting, who/what is working it, the branch or worktree, and the initial plan of attack.
- **While working:** meaningful progress, decisions made and why, dead ends ruled out, surprises found, scope changes. If it took you more than a few minutes to figure out, it's worth a comment.
- **On stop (pausing, not done):** a handoff-quality state dump — what's done, what remains, where the work lives (branch/commit/PR), any gotchas, and the exact next step to take when picking it back up.
- **On close:** the closing evidence — what changed, links to PR/commit/deploy, how it was verified, remaining risk, follow-ups created.
- **Any other time it helps:** blockers, questions for the user, cross-links to related issues. When in doubt, comment.

## Style
- Lead with a short bold header naming the moment (e.g. **Started**, **Progress**, **Pausing**, **Closed**) so the timeline scans easily.
- Include links: PRs, commits, branches, deploys, related issues, docs. A claim with a link beats a claim without one.
- Write for a cold reader — no session-local shorthand; spell out what "it" and "the fix" are.
- Comments are cheap, lost context is expensive. It's OK to be heavy.
