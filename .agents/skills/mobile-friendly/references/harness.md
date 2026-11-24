# The harness: a private preview per agent

**Why:** a layout loop lives or dies on the time from edit to screenshot. A production build takes minutes, and on a shared machine one agent's rebuild of the shared bundle replaces the page every other agent is looking at. So each agent gets its own dev server with hot reload, on its own port, built from its own worktree, and every dev server talks to the one shared backend through a proxy. Edits show in about a second, and agents never see each other's half-done CSS.

## Shape

```
agent worktree ──(sync)──▶ private app tree ──▶ dev server :53NN (hot reload)
                                                     │ proxy /api, /ws, /auth …
                                                     ▼
                                       shared local backend (one for all agents)
```

1. **Base tree once per dependency set.** Install the frontend dependencies once into a base tree (`node_modules`, a few hundred MB). Each agent's app tree is a hard-link copy of the base (`cp -al base app`): seconds, almost no disk. Package managers and editors replace files (write a new file, rename it), so an edit in one copy does not leak into another. Give each dev server its own cache directory (Vite: `cacheDir`), or they rewrite each other's prebundled deps.
2. **Sync, do not symlink.** When the app is assembled from several sources (an upstream tree plus an overlay), copy the agent's sources over its app tree with `rsync -a` after each edit. The dev server's file watcher picks up the copy. Symlinks confuse watchers and module resolution.
3. **Proxy the backend paths.** The dev server serves the frontend and forwards exactly the paths the production reverse proxy sends to the backend (read them from that proxy's config, do not guess). Forward websockets too. When the backend uses a local TLS certificate, point Node at its root (`NODE_EXTRA_CA_CERTS`) instead of switching verification off.
4. **Sign in without the identity provider.** If the backend has a development login that mints tokens, mint one through the preview's own proxy and write it where the frontend keeps its session (`sessionStorage`/`localStorage`) before you open the page. Storage is per origin, so do this on each preview port.
5. **Detach the server properly.** Start it in its own process group (`setsid nohup … &`), write the pid, and stop it by group (`kill -- -<pid>`). A server started from an agent's shell call may die when the call returns, or outlive the agent and hold its port.
6. **Ports and sessions are assigned, not chosen.** The coordinator hands each agent one port and one browser session name. Two agents on one port means one sees the other's page.

## Cost

One dev server (~300–500 MB) plus one headless browser (~0.5–1 GB) per agent. Check free memory and load before you start 16 of them; on a shared box, keep headroom for everyone else.

## Viewport and device

- `agent-browser set viewport <w> <h> 2` sets width, height and pixel ratio (2 gives crisp screenshots).
- `agent-browser set device "iPhone 14"` also sets the user agent (apps that sniff it change behaviour), but **not touch**: `(any-pointer: coarse)` stays false and `navigator.maxTouchPoints` is 0. Do not rely on it to test touch-only CSS.
- `agent-browser set media dark|light` sets `prefers-color-scheme`; apps with their own theme toggle may ignore it.
- Text at 200 %: there is no agent-browser switch; set `document.documentElement.style.fontSize = "200%"` in `eval` for a rough check of `rem`-based text (it does not scale `px`, which is the point: `px` text that does not grow is a fault).
