# The harness: a private local preview per agent

**Why:** a layout loop lives or dies on the time from edit to screenshot. It should be milliseconds, at worst a few seconds. A production build takes minutes and a cloud deploy can take an hour, and on a shared machine one agent's rebuild of the shared bundle replaces the page every other agent is looking at. So each agent gets its own dev server with hot reload, on its own port, built from its own worktree, on the local machine, and every dev server talks to one shared local backend through a proxy. Edits show in about a second, and agents never see each other's half-done CSS. The cloud is only the final parity check ([fan-out.md § parity](fan-out.md#4--integrate-then-check-parity)).

## Shape

```
agent worktree ──(sync)──▶ private app tree ──▶ dev server :53NN (hot reload)
                                                     │ proxy /api, /ws, /auth …
                                                     ▼
                                       shared local backend (one for all agents)
```

1. **Base tree once per dependency set.** Install the frontend dependencies once into a base tree (`node_modules`, a few hundred MB). Each agent's app tree is a copy of the base. Hard links (`cp -al`) are fast and cost almost no disk, but they share inodes: a tool that rewrites a file in place changes the base and every sibling. Share only dependencies nobody writes (`node_modules`), copy the sources (`rsync`, or `cp --reflink=auto` on a filesystem that supports it), and give each dev server its own cache directory (Vite: `cacheDir`), or they rewrite each other's prebundled deps.
2. **Warm the base before you clone it.** The first page load makes each dev server prebundle the dependencies and compile every module. Sixteen cold servers at once drove one 32-core machine to a load of 34 and made first loads take over a minute. Start one server on the base, load one page, stop it, then clone: every copy starts with the prebundle.
3. **Sync, do not symlink.** When the app is assembled from several sources (an upstream tree plus an overlay), copy the agent's sources over its app tree with `rsync -a` after each edit. The file watcher picks up the copy. Symlinks confuse watchers and module resolution.
4. **Proxy the backend paths.** The dev server serves the frontend and forwards exactly the paths the production reverse proxy sends to the backend (read them from that proxy's config, do not guess). Forward websockets too. When the backend uses a local TLS certificate, point Node at its root (`NODE_EXTRA_CA_CERTS`) instead of switching verification off.
5. **Frontend and backend versions must match.** The shared local backend may be older than the frontend in a fresh worktree. A page that renders an error boundary on first load ("cannot read properties of undefined") is a missing field from an older API, not a layout fault. Rebuild the local backend from the same branch, or check that page against a backend that matches; do not patch around it in the page.
6. **Serve on the host name the app's dev auth expects.** Apps often enable local sign-in or fake signing only for `localhost`, not `127.0.0.1`: open the preview on the same host name, or actions such as an e-signature fall through to the real identity provider. Store the token's own subject as the user, so ownership checks see one identity.
7. **Sign in without the identity provider.** If the backend has a development login that mints tokens, mint one through the preview's own proxy (it already trusts the local certificate) and write it where the frontend keeps its session (`sessionStorage`/`localStorage`) before you open the page. Storage is per origin, so do this on each preview port. A login that a reload loses: run the login step again.
8. **Detach the server properly.** Start it in its own process group as a *simple command*: `cd app`, then `setsid nohup <server> >log 2>&1 &` on its own line, then `echo $! >pid`. Stop it by group (`kill -- -<pid>`). `$!` after a backgrounded list (`(cd app && setsid … &)`) is the subshell, not the server: the stop then kills a dead pid and the server keeps its port. Never `pkill -f <pattern>` in a shell whose own command line holds the pattern: it kills itself. Hold one lock per worktree across start and stop, and do not let the server inherit it (`8>&-` on the spawn). In bash, `set -e` does not reach inside `$(...)` unless `shopt -s inherit_errexit`: without it, a failed base build inside a command substitution still runs its final `mv` and publishes a broken base.
9. **Ports and sessions are assigned, not chosen.** The coordinator hands each agent one port and one browser session name. Two agents on one port means one sees the other's page.
10. **Prove it before you hand it out**: start, sign in, open a page with real data at 390 px, edit one style, see it change, stop, port closed. Write the exact commands into the brief.

## Borrow data, never move the loop

A state the local stack cannot show (an editor in edit mode, rows that need a finished pipeline, a chart that needs history) is a tooling gap, not a reason to check on the cloud. Copy one record from a deployed environment onto localhost and keep the loop local:

- **Capture through the app's own read APIs**, one named record at a time, paced for the gateway; never a raw database dump. Downloads through the app may write audit records on the source environment.
- **Borrow only data approved for development use**: synthetic or sanitized test records, with their related data (roster profiles, attachments) checked too. Leave out credentials and sensitive attachments, keep the capture in an ignored local folder, delete it when the work ends, and keep borrowed personal data out of screenshots you share.
- **Import through the app's APIs or one importer per table family**, with the same identities on the roster (owner, editor, reviewer) so permission checks still hold.
- **Guard the import target hard, and fail closed**: before connecting, refuse any host that is not the local service; after connecting, require a positive identity of the disposable local database (a marker the local provisioning writes, such as a sentinel row or a database comment, checked against the expected value) and refuse a server that carries a cloud-only marker. A host name, a port or a missing marker alone can be spoofed (a local port can forward to a remote database).
- **Expect version drift**: the deployed API may be ahead or behind the local one (a lock `schema_version`, a renamed endpoint). Map it in the importer, not by hand.
- **Know the gaps**: append-only or run-history tables (simulations, agent runs) are the expensive part; name them instead of faking them.

## Cost

One dev server (~300–500 MB) plus one headless browser (~0.5–1 GB) per agent. Check free memory and load before you start 16 of them; on a shared box, keep headroom for everyone else, and warm the base (item 2).

## Driver traps (agent-browser 0.27)

- `set viewport <w> <h> 2` sets width, height and pixel ratio (2 gives crisp screenshots). Opening or signing in can reset the viewport: set it **after** the page is open, and check `viewport.w` in the probe output.
- `set device "iPhone 14"` also sets the user agent (apps that sniff it change behaviour), but **not touch**: `(any-pointer: coarse)` stays false and `navigator.maxTouchPoints` is 0.
- `set media dark|light` sets `prefers-color-scheme`; apps with their own theme toggle may ignore it.
- `wait "<css selector>"` is reliable; `wait "text=…"` timed out with the text on screen. `click "text=…"` can miss too: click by ref from `snapshot -i`, or `eval` a click on the element.
- `screenshot --full` captures the document. When the app scrolls inside its own container, it shows only the first screen: scroll the container and shoot in steps.
- An init script (to stub something before the page loads) goes in `AGENT_BROWSER_INIT_SCRIPTS=<path>` before the open; wrap it in an IIFE.
- In sandboxed agent shells, plain `sleep` and `npx -y <pkg>@latest` may be blocked: use `agent-browser wait <ms>` and the web versions of the guides.
- Long commands hit the tool's time limit: run start, sign-in and viewport as separate calls, each under `timeout`.

## Text size and zoom

Four different conditions; do not let one stand in for another:

- **Reflow (WCAG 1.4.10):** a 320 px wide layout (the phone loop already covers it) and, for one-direction horizontal content, a short viewport (256 px high).
- **Desktop page zoom at 200 %:** the layout viewport halves in both directions. Emulate it with half the desktop width **and** half its height (1280 × 800 → 640 × 400): nothing may overflow, overlap or hide behind a fixed bar.
- **Phone pinch zoom:** enlarges the visual viewport only; the layout does not change. Check that zoom is not blocked (`meta.zoomBlocked` is 0) and that fixed bars do not cover the zoomed content.
- **System text size** (iOS Dynamic Type, Android font scale): scales `rem`/`em`-based text where the browser maps it to the root size. Set `document.documentElement.style.fontSize` to twice the app's root size in `eval`: text containers must grow (minimum heights, never fixed heights). Text in `px` does not grow here; that is a finding to weigh, not automatically a fault.
