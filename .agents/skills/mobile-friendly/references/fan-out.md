# Fanning out: one agent per page

**Why:** a page-by-page pass done by one agent runs out of attention by the fifth page and starts approving what it would have fixed on the first. One agent per page keeps each critique fresh, runs the pages in parallel, and gives each branch one owner. The price is collisions on shared code, which the ownership rules below prevent.

## 0. 📋 Inventory every page the app serves

- **Read the tree the agents will branch from**, not whatever checkout is at hand: a stale checkout gave the first campaign a page file that no longer existed and missed five routes.
- **Two sources, reconciled:** the router (route tables, file routes, routes a framework or upstream package adds) and the navigation list the user sees (sidebar, menu). The router finds admin and deep pages the menu hides; the menu finds framework pages the app's own route file does not declare.
- For each route record: path pattern, the component it renders, a record id **with real data** (an empty project hid every row-level fault on one page), the role it needs, and the user who can see it (a member of that record).
- **Classify before assigning:**
  - *owns a layout* → one page agent per component (routes that render the same component share one agent);
  - *redirect only* or *a title plus a shared panel* → the shell owner (three page agents in the first campaign found nothing of their own to fix);
  - *page file with no route* → not a page: report it as dead code;
  - *owned by an upstream package* (served by the app but maintained elsewhere) → an agent that edits upstream and previews the change locally, with the upstream's own review.
- A page that depends on browser state (a "last project" redirect) behaves differently in a fresh browser profile: note which state the agent should see.

## 1. 🧭 Ownership

| Owner | Files |
|-------|-------|
| **Shell agent** | the app frame: top bar, menu drawer, page header and its actions slot, back link, page margin, global CSS and tokens, and the shared components most pages use (buttons, fields, pills, pagination, tables, state panels, segmented controls) |
| **Page agent** | the page's own component folder and the CSS it alone imports |
| **Coordinator** | inventory, the brief, relaying shared faults to the shell agent, showing the user, integration, the ledger |

A page agent that needs a shared change writes it in its report (*file, change, why, which pages it helps*) and does not make it. Before editing a file, a page agent checks who else imports it; more than its own page means it is shared. The coordinator forwards shared faults to the shell agent **while it is still running**, so they land in one place once.

**Check who owns the frame before you change it.** Another session may be redesigning the header or layout at the same time; a shell fix built on the old structure conflicts on merge. Ask the frame's owner, hand over the rule and the reference branch, and let one owner implement it; then re-run the sweep when it lands.

**Shell first.** Every page agent in the first campaign reported the same frame faults (the header row, the side margin, the back-link target, `100vh`). Give the shell agent a head start of one full round, then start the page agents on the fixed frame; their screenshots then show their own faults, not the frame's.

## 2. ✉️ The brief

Write one shared brief file and give each agent a short prompt that points at it plus its assignment. The brief carries:

- the research step and the cited take-aways from the coordinator's research ([research.md](research.md));
- the exact, proven harness commands and the known traps ([harness.md](harness.md));
- the rules source: this skill's [checklist](checklist.md) plus the project's own phone rules file, which wins;
- the loop ([loop.md](loop.md)) with the probe path and the page-root selector;
- the ownership rule and the "do not touch" list;
- read-only rules for shared data (which buttons never to press);
- screenshot naming and folder, so the coordinator can show the user every shot;
- the stop rule and the report format;
- the project's code rules for CSS and components (tokens, comment style, no new dependencies);
- cleanup: stop the preview server and close the browser session.

Each prompt carries: the route(s) and component, the record id and user, worktree, branch, port and session name, and the agent's files. Update the brief when the first reports bring new traps; tell the running agents to re-read it.

## 3. ⚖️ Capacity

One dev server plus one headless browser per agent ([harness.md § cost](harness.md#cost)). Warm the base first. Watch load and free memory while they run; reap stray browsers and dev servers after (match their worktree paths, not a broad pattern).

## 📣 Show the user while it runs

Watch the screenshot folders. Each time new shots land, send them to the user in the chat as images with a one-line caption: first every page's *before*, then each page's iterations and *after* as they come. Do not wait for an agent to finish to show its work; do not batch everything into one gallery at the end.

## 4. 🔗 Integrate, then check parity

1. Merge the page branches one by one into an integration branch; a conflict means two owners touched one file: keep both intents, then tell the ledger.
2. Run the typecheck and the build once on the merged tree.
3. Start one local preview from the merged tree and run the probe on **every** page at 390 px (and 320 for the worst ones), with and without the page root. One table: page × count, before and after.
4. Shoot every page at 390 px and 1280 px and send them: the desktop layout must not have moved.
5. Review the diff with a second reader before merge, as any change.
6. **Parity check on the deployed environment** after the deploy: the same pages, the same widths, the same probe. The result should match localhost. A difference (fonts not loaded, a different CDN asset, real data with longer names, a gateway banner) is a finding for the ledger, not a reason to iterate on the cloud.

## 5. 📒 Fold back

Collect every agent's "Findings for the skill" lines into [findings.md](findings.md) under the campaign's date. Then promote:

- a fault class that two or more pages hit → a rule in [checklist.md](checklist.md) or a sharper threshold;
- a fix that worked twice → a pattern in [fixes.md](fixes.md);
- a probe false positive or miss → a change to [`mobile-probe.js`](../scripts/mobile-probe.js), tested on the page that showed it;
- a harness or driver trap → [harness.md](harness.md);
- a research source that changed a fix → [research.md](research.md).

Keep findings provider-neutral here (the framework and the fault, not the product); product-specific rules go into the project's own design file.
