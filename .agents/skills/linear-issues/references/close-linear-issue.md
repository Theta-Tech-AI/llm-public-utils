---
name: close-linear-issue
description: Close out an existing issue.
---

# Close Linear Issue
1. **Connect:** Connect to Linear MCP (if it is not up or authorized, set it up per [connect.md](connect.md)).
2. **Identify:** Pin down exactly which issue the user wants to close, per the Quick Orient section of [orient.md](orient.md). If they gave you an identifier or link, fetch it directly.
3. **Verify Done:** Re-read the issue's "what does done look like?" criteria and its comments. Make sure the work is actually complete — check the linked PRs, commits, branches, or deploys as needed. If something in the done criteria is not met, tell the user what's missing and ask whether they want to close anyway (with a stated reason), keep it open, or split the remainder into a follow-up issue. Asking the user clarifying questions is optional, not required, when done-ness is obvious.
4. **Pick the Right Resolution:** Not every close is "Done". Decide with the user if needed which closed state honestly reflects what happened, per the Status honesty rules in [issue-standards.md](issue-standards.md).
5. **Closing Comment:** Before flipping the status, leave a closing comment with the evidence, per [comment-rules.md](comment-rules.md): what was done, links to the PR/commit/deploy that resolved it, how it was verified, and any remaining risk or follow-up issue you created. A bare status flip with no comment is bad hygiene.
6. **Close:** Update the issue's status via MCP to the chosen closed state. Follow the requirements listed below.
7. **Sweep Related:** Check for related items the close affects: sub-issues still open, a parent issue now unblocked, duplicates that should be closed alongside, blocked issues whose blocker just cleared. Handle or surface each one — don't leave orphans.
8. **Rendering Ticket:** After the issue is closed, render it for the user per [render-ticket.md](render-ticket.md).

## Requirements
Closing a Linear issue requires all of the following (on top of [issue-standards.md](issue-standards.md)):
- Correct resolution state per the Status honesty rules
- A closing comment with evidence: what changed, links to PR/commit/deploy, how it was verified
- Done criteria checked against the issue's original "what does done look like?" — or an explicit user-approved reason for closing without meeting them
- Duplicates linked to the surviving issue
- Any remaining work captured as a follow-up issue (see create-linear-issue.md) and cross-linked, never silently dropped
- Related issues swept: sub-issues, parent, and blocked issues updated or surfaced
