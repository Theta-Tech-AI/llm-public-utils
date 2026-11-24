# Fanning out: one agent per page

**Why:** a page-by-page pass done by one agent runs out of attention by the fifth page and starts approving what it would have fixed on the first. One agent per page keeps each critique fresh, runs the pages in parallel, and gives each branch one owner. The price is collisions on shared code, which the ownership rules below prevent.

## 0. 📋 Inventory from the router

Read the router (route table, file-based routes), not the menu: the menu hides admin pages, project-scoped pages and pages reached only by a link. For each route, record: path pattern, the page component, whether it is a redirect only (no agent), whether it needs a record id (pick one with real data), whether it needs a role (admin pages). Group routes that render the same component; one agent per component, not per path.

## 1. 🧭 Ownership

| Owner | Files |
|-------|-------|
| **Shell agent** | the app frame: top bar, menu drawer, page header, breadcrumbs, global CSS, design tokens, the shared components most pages use (buttons, cards, dialogs, tables) |
| **Page agent** | the page's own component folder and the CSS it alone imports |
| **Coordinator** | integration, the probe table across pages, the skill ledger |

A page agent that needs a shared change writes it in its report (*file, change, why, which pages it helps*) and does not make it. The coordinator hands those to the shell agent, or makes them once at the end. Before editing a file, a page agent checks who else imports it (`grep` for the import); more than its own page means it is shared.

## 2. ✉️ The brief

Each agent's brief carries, at minimum:

- the page: route, component path, a record id with real data, the role it needs;
- its worktree path, branch name, preview port and browser session name (all assigned);
- the rules source: this skill's [checklist](checklist.md) plus the project's own phone rules file, which wins;
- the loop: [loop.md](loop.md), with the probe path;
- the ownership rule and the "do not touch" list (shell files, other pages);
- the stop rule (happy test, or three iterations without progress) and the report format ([loop.md § 6](loop.md#6--report));
- the project's code rules that apply to CSS and components (tokens, comment style, no new dependencies);
- cleanup: stop the preview server and close the browser session at the end.

Prove the harness on one page yourself before you send any brief: the exact start, sign-in and screenshot commands, with the output. An agent that has to debug the harness spends its budget there and never reaches the page.

## 3. ⚖️ Capacity

One dev server plus one headless browser per agent ([harness.md § cost](harness.md#cost)). Start the shell agent first, or together with the page agents under the "do not touch the shell" rule. Watch the machine (load, free memory) while they run; reap stray browsers after.

## 4. 🔗 Integrate

1. Merge the page branches one by one into an integration branch; a conflict means two owners touched one file: keep both intents, then tell the ledger.
2. Run the typecheck and the build once on the merged tree.
3. Start one preview from the merged tree and run the probe on **every** page at 390 px (and 320 for the ones that were worst). One table: page × count, before and after.
4. Shoot every page at 390 px and 1280 px: the desktop layout must not have moved.
5. Review the diff with a second reader before merge, as any change.

## 5. 📒 Fold back

Collect every agent's "Findings for the skill" lines into [findings.md](findings.md) under the campaign's date. Then promote:

- a fault class that two or more pages hit → a rule in [checklist.md](checklist.md) or a sharper threshold;
- a fix that worked twice → a pattern in [fixes.md](fixes.md);
- a probe false positive or miss → a change to [`mobile-probe.js`](../scripts/mobile-probe.js), tested on the page that showed it;
- a harness trap → [harness.md](harness.md).

Keep findings provider-neutral here (the framework and the fault, not the product); product-specific rules go into the project's own design file.
