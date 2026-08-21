---
name: stop-linear-issue
description: Pause work on an issue that isn't done yet (e.g. stopping for the day).
---

# Stop Linear Issue (pause, not close)
This is for when the user is stopping work — end of day, switching tasks, blocked — but the issue is NOT done. Closing is a different action (see close-linear-issue.md); stopping must leave the issue in a state where anyone (including a future you with no memory of this session) can pick it up cold.

1. **Connect:** Connect to Linear MCP (if it is not up or authorized, set it up per [connect.md](connect.md)).
2. **Orient:** Confirm which issue is being paused, per the Quick Orient section of [orient.md](orient.md). Usually it's the one you've been working, but confirm if ambiguous.
3. **Park the Work:** Make sure nothing lives only in your session — commit and push the branch (even WIP, clearly marked as such), and link any draft PR. Uncommitted work at stop time is work that can be lost.
4. **Stopping Comment:** This is the heart of stopping. Leave a handoff-quality state dump per [comment-rules.md](comment-rules.md): what's done, what remains, where the work lives (branch/commit/PR), any gotchas discovered, and the exact next step to take on resume. Write it for a cold reader — the continue action (continue-linear-issue.md) will rehydrate from exactly this comment.
5. **Status & Blockers:** Leave the status honestly reflecting reality — typically it stays In Progress; if you stopped because you're blocked, mark it blocked and link the blocking issue. Update the due date if the pause makes it unrealistic, and flag that to the user.
6. **Rendering Ticket:** Render the paused issue for the user per [render-ticket.md](render-ticket.md) — include the state-dump gist and the next step, maybe a ⏸️, so the user ends the session knowing exactly where things stand.
