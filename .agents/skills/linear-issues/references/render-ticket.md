---
name: render-ticket
description: How to render a Linear issue for the user after an action.
---

# Rendering a Ticket
After acting on an issue (creating it, closing it, etc.), give the user a concise summary of the issue: a hyperlink, all the tags and labels, maybe colors if you can, a brief synopsis, maybe ascii borders. If you're on a tui you have a lot of ways to render the issue for the user graphically with rgb fonts, unix chars, emojis, etc, so make use of it and show the user a rendered ticket. Be an artist here.

Tailor the rendering to the action:
- **Created:** show the new ticket — title, project, assignee, due date, labels, done criteria.
- **Started:** show the ticket with its new In Progress status (maybe a 🚀), the branch/worktree, and the plan of attack.
- **Continued:** show the ticket with a brief "where we left off / what's next" so the user is re-oriented too.
- **Stopped (paused):** show the ticket with the state-dump gist and the next step on resume (maybe a ⏸️).
- **Closed:** show the final status (maybe with a satisfying ✅), the closing comment gist, and any follow-ups created.
