---
name: continue-linear-issue
description: Resume work on an issue that was previously started.
---

# Continue Linear Issue
1. **Connect:** Connect to Linear MCP (if it is not up or authorized, set it up per [connect.md](connect.md)).
2. **Orient:** Get your bearings and pin down which in-progress issue the user wants to resume, per the Quick Orient section of [orient.md](orient.md). If unclear, offer a multiple choice selection of their In Progress issues.
3. **Rehydrate:** Read the issue's comments from the top — especially the most recent stop/pause comment, which should contain the state dump: what's done, what remains, where the work lives, and the exact next step. Also check the linked branch/PR and recent commits so your picture matches reality, not just the last comment.
4. **Reconcile:** If reality has drifted from the last comment (someone else pushed, a blocker cleared or appeared, requirements changed in newer comments), reconcile before continuing and surface anything surprising to the user.
5. **Resuming Comment:** Leave a comment that work is resuming, per [comment-rules.md](comment-rules.md) — what you're picking up from and the immediate next step.
6. **Continue:** Pick up from the recorded next step. Keep commenting as you work per [comment-rules.md](comment-rules.md).
7. **Rendering Ticket:** Render the resumed issue for the user per [render-ticket.md](render-ticket.md) — include a brief "where we left off / what's next" so the user is re-oriented too.
