---
name: start-linear-issue
description: Pick up an issue and start working on it.
---

# Start Linear Issue
1. **Connect:** Connect to Linear MCP (if it is not up or authorized, set it up per [connect.md](connect.md)).
2. **Orient:** Get your bearings and pin down exactly which issue the user wants to start, per the Quick Orient section of [orient.md](orient.md). If the user didn't name one, propose candidates from their open issues (due soon, overdue, or high priority first) as a multiple choice selection.
3. **Understand:** Read the issue in full — description, comments, links, sub-issues, blockers. Make sure you understand what done looks like before writing any code. If the issue is missing required fields or the done criteria are unclear, fix that now per [issue-standards.md](issue-standards.md) rather than starting on a vague ticket.
4. **Check Blockers:** If the issue is blocked by another open issue, surface that to the user before starting — they may want to work the blocker first.
5. **Claim & Status:** Assign the issue (if not already assigned correctly) and move it to In Progress (or the team's equivalent started state).
6. **Starting Comment:** Leave a comment that work is starting, per [comment-rules.md](comment-rules.md) — who/what is working it, the branch or worktree, and the initial plan of attack.
7. **Set Up:** Create the feature branch / worktree as the repo's conventions dictate, so the work has a home from minute one.
8. **Rendering Ticket:** Render the started issue for the user per [render-ticket.md](render-ticket.md).

While you work, keep commenting per [comment-rules.md](comment-rules.md) — progress, decisions, dead ends, surprises.
