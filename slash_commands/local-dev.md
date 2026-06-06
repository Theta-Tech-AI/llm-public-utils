---
description: Bring up a local/hybrid dev stack (Postgres + vector store + FastAPI + reverse proxy + SPA locally, optional remote LLM provider) so you can iterate on frontend + backend + agent changes without a cloud redeploy.
---

# /local-dev — bring up a hot-iteration local stack

Stand up the upstream framework's docker-compose stack with your overlay tree applied, so you can edit frontend / backend code and see the change locally within seconds. By default this is local-only and uses fake-auth / fake-LLM mode. For agentic loops (classification, retrieval ranking, writer/generation quality), prefer **hybrid local-dev**: keep Postgres, the vector store, FastAPI, the reverse proxy, and the SPA local, but route LLM calls to your remote LLM provider using local-only secrets. This still does not deploy to your cloud environment and does not use cloud Postgres / vector store / object storage. It's for the inner loop: edit → reload → see → fix → repeat.

**Run this against your working branch** (the daily integration branch — e.g. `development`). That's the source of truth for "what code looks like right now." A promotion branch (e.g. `staging`) is a deploy target, NOT a working branch — only merge the working branch into it when you want to deploy to the cloud. So before invoking `/local-dev`:

```bash
git checkout development
git pull --ff-only
```

If you have in-flight edits you want to test locally, commit them on the working branch first, then iterate. Don't push to the promotion branch until you're ready to promote.

## What this command produces

After running, you will have:
- A docker-compose stack running on the laptop (Postgres on `127.0.0.1:5432`, the vector store on `:8081/:50052`, the FastAPI api on `:8000` behind the reverse proxy on `:8443`).
- Your frontend overlay applied (brand colors, logo, nav structure, sign-in bounce guards).
- Your backend overlay rsynced in (identity-provider verifier, secrets provider, object-storage ingestion, etc. — but inactive because `AUTH_PROVIDER=fake` etc.).
- The SPA reachable at `https://localhost:8443/` (self-signed cert; browser warning is expected).
- Optional remote-LLM-backed model calls against the local API, so agent workflows can be tested without waiting on a cloud deploy.
- A documented fast-iteration loop for frontend + backend changes.

## What this command does NOT do

- Deploy to your cloud environment. No infra templates, no gateway/load-balancer/VM roll, no cloud database mutation.
- Read your cloud secret store or depend on cloud Postgres / vector store / object storage. If hybrid LLM is enabled, put the LLM endpoint/key/deployment in local-only ignored env, not in tracked files.
- Provide real LLM responses unless explicitly configured. Default remains `LLM_PROVIDER=fake`. For agentic flows, configure your remote LLM provider locally and keep every other dependency local.
- Provide real authentication (`AUTH_PROVIDER=fake`, so `/dev/login` mints a JWT no real human needs to see).

## Prerequisites (verify before running anything)

Run these as a single batch first:

```bash
echo "== docker + compose =="
docker --version 2>&1 | head -1
docker compose version 2>&1 | head -1
echo
echo "== node + npm (only needed for frontend hot-reload) =="
node --version 2>&1
npm --version 2>&1
echo
echo "== submodule initialized? =="
git submodule status upstream-framework | head -1
echo
echo "== ports 5432 / 8081 / 8443 free? =="
for p in 5432 8081 8443 8088; do
  ss -ltn "sport = :$p" 2>/dev/null | grep -q LISTEN && echo "  :$p IN USE" || echo "  :$p free"
done
```

If the submodule shows a leading `-` (uninitialized), run `git submodule update --init --recursive` first. If a port is in use, override via `DEV_HTTPS_PORT=<other>` in step 4.

## Setup steps

**1. Rsync your frontend overlay for pure fake-mode UI work.** The backend overlay is not needed for layout-only work: it imports cloud SDKs (object storage, identity, secret store, etc.) that are only installed if the dev image has the cloud deps listed in the hybrid section below. The frontend overlay is safe — it's just TypeScript / TSX / CSS / asset replacements; Vite consumes them with no extra deps.

```bash
rsync -a overlays/files/frontend/ upstream-framework/frontend/
# Verify backend overlay is NOT in place (it would break pure fake-mode dev):
git -C upstream-framework status --short | grep -E 'backend/src/services/(auth/provider|secrets/cloud|object_kb|llm)' | head -3
# Expect: 0 lines. If any of those paths show up dirty, undo them:
#   git -C upstream-framework checkout backend/src/services/auth/provider backend/src/services/secrets/cloud backend/src/services/object_kb backend/src/services/llm 2>/dev/null
```

For classification, retrieval, source-upload, or writer work, use the hybrid path below and rsync the backend overlay too.

### Hybrid remote-LLM mode discovered requirements

The "frontend overlay only" rule is correct for pure fake-mode UI work, but it is not enough for hybrid LLM/agent testing. If `LLM_PROVIDER=remote`, the local API must run with your backend overlay applied because the remote-LLM client, classification routes, object-store tenant policy, and the workflow routers live under your overlay tree.

Current proven local shape:

```bash
rsync -a overlays/files/frontend/ upstream-framework/frontend/
rsync -a overlays/files/backend/  upstream-framework/backend/
```

The upstream local image installs `upstream-framework/backend/requirements.txt`, not the cloud-extras requirements file. Hybrid mode therefore needs the cloud-SDK dependencies present before the image build (whatever your remote provider's SDK requires), for example:

```text
cloud-secrets-client>=4.8.0,<5.0
cloud-object-storage>=12.20.0,<13.0
```

Do not put secrets into tracked files. Use an ignored local compose override under `build/` or an ignored `deploy/.env.local`. At minimum the API needs:

```yaml
services:
  api:
    environment:
      LLM_PROVIDER: remote
      ARBITER_ENDPOINT_URL: http://arbiter:8080
      LLM_ENDPOINT: https://<your-llm-account>.example-llm.com
      LLM_DEPLOYMENT_NAME: <your-model-deployment>
      LLM_TENANT_ID: <tenant>
      LLM_CLIENT_ID: <local service principal>
      LLM_CLIENT_SECRET: <local secret>
      QUALITY_REVIEWER_GROUP: qr-dev
      # Needed for source-upload E2E. `fake` storage is read-only and
      # raises NotImplementedError on upload/find-folder paths.
      STORAGE_PROVIDER: cloud_object
      OBJECT_KB_STORAGE_ACCOUNT: <storage account>
      STORAGE_ACCOUNT_NAME: <same storage account>
      OBJECT_KB_CONTAINER: knowledge
      KNOWLEDGE_SOURCE_PROVIDER: fake
      SEARCH_KB_TENANT: kb_tenant_default
      SHARED_KB_TENANTS: kb_tenant_default
      OBJECT_KB_ALLOWED_TENANTS: kb_tenant_default
      OBJECT_KB_ALLOWED_TENANT_PREFIXES: kb_tenant_
```

Hybrid mode also needs the API container on an egress-capable network.
The base upstream compose intentionally attaches `api` only to the
`internal` network; that is correct for fake-mode but blocks DNS and
HTTPS egress to your identity provider, object storage, and LLM
endpoint. In the ignored local override, attach `api` to both networks:

```yaml
services:
  api:
    networks:
      - edge
      - internal
```

If you only need local browser/API smoke tests and do **not** have local
LLM secrets loaded in the current shell, do not start the hybrid
override as-is: it sets `LLM_PROVIDER=remote`, and the API will
crash-loop with `LLM_ENDPOINT is unset`. Add a temporary fake-LLM
override after the hybrid file:

```bash
cat >/tmp/local-fake-llm.override.yml <<'YAML'
services:
  api:
    environment:
      LLM_PROVIDER: fake
      LLM_ENDPOINT: ""
      LLM_DEPLOYMENT_NAME: ""
      LLM_CLIENT_ID: ""
      LLM_CLIENT_SECRET: ""
      LLM_TENANT_ID: ""
YAML

cd upstream-framework/deploy
DEV_HTTP_PORT=18088 \
DEV_HTTPS_PORT=18443 \
docker compose -p localdev --env-file dev.env \
  -f docker-compose.yml \
  -f dev.docker-compose.yml \
  -f ../../build/local-dev.hybrid.override.yml \
  -f /tmp/local-fake-llm.override.yml \
  up -d --no-deps api
```

Use this fake-LLM fallback for route gating, auth, layout, audit, and
non-agentic regression checks. Use real hybrid LLM only when testing
classification, retrieval, comparison, or writer generation quality.

For source-upload E2E, prefer a local object-storage emulator over a
live cloud storage account. A hardened cloud storage account is
typically private (public network access disabled), so a laptop /
container cannot upload to it directly even if the local service
principal has the right RBAC. Use the real remote LLM endpoint for LLM
calls, but use a local object-storage emulator for source files:

```yaml
services:
  object-store-emulator:
    image: object-storage-emulator:latest
    command: emulator-blob --host 0.0.0.0 --loose --skipApiVersionCheck
    ports:
      - "127.0.0.1:10000:10000"
    networks:
      - edge

  api:
    depends_on:
      object-store-emulator:
        condition: service_started
    environment:
      STORAGE_PROVIDER: cloud_object
      STORAGE_CONNECTION_STRING: DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=<emulator-well-known-key>;BlobEndpoint=http://object-store-emulator:10000/devstoreaccount1;
      OBJECT_AUTO_CREATE_CONTAINER: "true"
      OBJECT_KB_CONTAINER: knowledge
```

Source indexing also needs a local stand-in for the GPU/reranker
service. The upstream dev compose sets `ARBITER_ENDPOINT_URL` at an
unresolvable fake host. That is fine for fake-mode but makes real
source indexing fail after document chunking. Add a local arbiter
service in the ignored override and point the API at it:

```yaml
services:
  api:
    environment:
      ARBITER_ENDPOINT_URL: http://arbiter:8080

  arbiter:
    image: app-api:dev
    entrypoint:
      - python
      - -m
      - uvicorn
      - src.services.arbiter.server_app:app
      - --host
      - 0.0.0.0
      - --port
      - "8080"
    depends_on:
      postgres:
        condition: service_healthy
      vector-store:
        condition: service_healthy
    networks:
      - internal
    environment:
      STAGE: dev
      LOG_FORMAT: text
      AUTH_PROVIDER: fake
      POSTGRES_HOST: postgres
      POSTGRES_PORT: "5432"
      POSTGRES_PASSWORD: ${DEV_POSTGRES_PASSWORD:-app-dev-password}
      VECTOR_STORE_HOST: vector-store
      VECTOR_STORE_GRPC_PORT: "50051"
      VECTOR_STORE_HTTP_PORT: "8080"
      VECTOR_STORE_WRITE_ROUTING_MODE: direct
      ARBITER_MAX_SYNC_WAITERS: "15000"
      RERANKER_URL: http://reranker.dev.fake:8090
      METRICS_ENABLED: "false"
```

This local arbiter has no GPU and no reranker, so `/health/ready` can
remain `503`/degraded because the reranker check is not satisfied. That
does not block source-upload indexing: the upload/chunk/upsert path uses
the arbiter's vector-store client and works without reranking. Reranking
quality is still a cloud validation concern unless a local reranker
service is added.

`STORAGE_CONNECTION_STRING` is local-dev only; when it is set, the
object-storage provider builds its client from the connection string and
skips cloud credentials. `OBJECT_AUTO_CREATE_CONTAINER=true` is also
local-dev only and exists so the emulator's `knowledge` container is
created on first API startup.

If Docker DNS inherits a host stub resolver and cannot resolve public
cloud hosts from inside the container, add explicit DNS servers in the
same ignored override:

```yaml
services:
  api:
    dns:
      - 1.1.1.1
      - 8.8.8.8
```

The local service principal must have object-storage-write permission on
the cloud storage account (or at least the `knowledge` container).
Without it, upload reaches storage with a valid token but fails with an
authorization 403. The credential-selection rule the provider must
follow: `LLM_CLIENT_ID + LLM_CLIENT_SECRET + LLM_TENANT_ID` means a
client-secret credential for local hybrid; a client id without a secret
means workload/managed identity for cloud. Treating any client id as
managed identity makes local upload hang/fail against the instance
metadata endpoint (`169.254.169.254`).

If another local app already owns `5432`, `8088`, or `8443`, do not edit `dev.env`. Export port overrides when starting compose:

```bash
DEV_HTTP_PORT=18088 \
DEV_HTTPS_PORT=18443 \
docker compose -p localdev --env-file dev.env \
  -f docker-compose.yml \
  -f dev.docker-compose.yml \
  -f ../../build/local-dev.hybrid.override.yml \
  up -d --build
```

Blockers observed while proving this out:

- A required env var (e.g. `QUALITY_REVIEWER_GROUP`) missing crashes the FastAPI lifespan.
- `LLM_PROVIDER=remote` without the backend overlay crashes with `No module named 'src.services.llm.remote'`.
- The backend overlay without object-KB tenant env crashes with `SEARCH_KB_TENANT is empty`.
- The classification agent uses its own LangChain-style model provider, not the app's shared invocation router. If classification agent calls hit 429/5xx bursts, verify `AGENT_MODEL_MAX_RETRIES` is present in the agent model provider and covered by a test; router retry tests alone do not cover this path.
- Adding `ports:` in an override does not replace the base compose's interpolated reverse-proxy ports; use `DEV_HTTP_PORT` and `DEV_HTTPS_PORT`.
- Uploading source docs with `STORAGE_PROVIDER=fake` crashes (the fake provider's `find_folder_by_name` is a stub for local dev); hybrid source-upload E2E needs `STORAGE_PROVIDER=cloud_object`.
- After an API container restart, localhost fake-auth signing keys change. Reload protected pages so the localhost `/dev/login` auto-mint path refreshes the SPA auth store before testing.
- `/dev/login` creates a new fake user UUID unless `user_id` is passed. If you are debugging an existing local locked project across restarts, pass a stable `user_id` or start a fresh project; otherwise the page can correctly report that a different local fake user owns the lock.
- The base compose `api` network is `internal: true`; hybrid cloud calls need the ignored override to attach `api` to `edge` as well.
- Docker DNS can fail inside the API container even when the host resolves cloud domains. Verify with `docker exec localdev-api-1 python -c "import socket; print(socket.gethostbyname('login.example.com'))"` and add explicit DNS in the override if needed.
- The local service principal needs object-storage RBAC before source upload works. Assign the write role and allow a few minutes for propagation.
- A hardened live storage account is not a good local upload target because public network access is disabled; use a local object-storage emulator plus `STORAGE_CONNECTION_STRING` for local source uploads.
- The current object-storage SDK can send an API version newer than the emulator supports; include `--skipApiVersionCheck` on the emulator command.
- The upstream dev stack points `ARBITER_ENDPOINT_URL` at a fake host. Real source indexing reaches that path after document conversion and fails unless the ignored override adds a local `arbiter` service and sets `VECTOR_STORE_WRITE_ROUTING_MODE=direct` inside it.
- Local arbiter startup logs can show GPU/reranker warnings on a non-GPU laptop/VM. Treat `GET /health/live -> 200` plus a successful source `upload_status=DONE` as the local source-indexing proof; do not require `/health/ready -> 200` until a local reranker is wired.

Verified local hybrid smoke:

```bash
# Stack shape: reverse proxy / API / Postgres / vector store /
# object-store emulator / arbiter local, LLM via remote provider,
# storage uploads via the local emulator.
curl -sk -X POST https://localhost:18443/dev/login ...
curl -sk -X POST https://localhost:18443/api/writing/projects ...
curl -sk -X POST https://localhost:18443/api/writing/projects/<project>/sources \
  -F file=@./sample-docs/example_source.pdf

# Poll result:
# upload_status=DONE, stage=DONE, chunk_count=36
```

**2. Create `upstream-framework/deploy/.env` from the dev template** (gitignored; safe defaults; no cloud values needed).

```bash
cd upstream-framework
[ -f deploy/.env ] || cp deploy/dev.env deploy/.env
```

If you want real LLM responses for testing, edit `deploy/.env` and add one of these local-only configurations.

Recommended for agent/classification/retrieval/writer loops (your remote LLM provider):

```
LLM_PROVIDER=remote
LLM_ENDPOINT=https://<your-llm-account>.example-llm.com/
LLM_API_KEY=<local secret, never commit>
LLM_DEPLOYMENT_NAME=<your-model-deployment>
```

Use a production-grade LLM deployment only when you explicitly want to spend that quota during local testing. Keep rate-limit behavior realistic: do not bypass the router retry/backoff layer; use the same LLM router path that cloud uses so 429 handling is exercised locally.

If you want a different LLM API for general testing, add the equivalent provider block, e.g.:

```
LLM_PROVIDER=other_api
OTHER_API_KEY=<key>
```
(Or export the key in the shell before `make up`.)

**3. Build the frontend dist with your overlay.** Vite reads the overlay-rsynced source files and produces a fresh `dist/`. This is what the reverse proxy serves on `https://localhost:8443/`.

```bash
cd upstream-framework/frontend
# Install deps (idempotent; ~30s warm, ~3min cold)
npm install
# Build with dev-appropriate env. Key flags:
#   VITE_SKIP_LANDING=true -- bypass the marketing landing on "/" and use
#     your RootRedirect overlay (authenticated -> /writing,
#     unauthenticated -> initiateLogin). Without it, "/" renders the
#     marketing landing whose "Sign In" button reads the same VITE_*
#     env vars below; if those are unset, the button leads to
#     `https://localhost:8443/undefined/oauth2/authorize?client_id=
#     undefined&...` -- a broken link.
#   VITE_AUTH_PROVIDER + VITE_OIDC_* point at your identity provider's
#     app registration. Sign-in via the hosted UI works from localhost
#     only if the redirect_uri https://localhost:8443/callback is
#     registered there first; for pure JWT-injected dev, this is moot.
#   AUTH_PROVIDER=fake on the BACKEND (deploy/.env) is independent --
#     it makes /dev/login mint JWTs the api accepts. The frontend never
#     sees that flag; inject the dev JWT via DevTools (snippet below)
#     and the SPA is happy.
VITE_AUTH_PROVIDER=oidc \
VITE_OIDC_TENANT_ID=<your-tenant-id> \
VITE_OIDC_CLIENT_ID=<your-client-id> \
VITE_API_BASE=https://localhost:8443 \
VITE_REDIRECT_URI=https://localhost:8443/callback \
VITE_SKIP_LANDING=true \
  npm run build
```

### Inject a dev JWT (avoid the identity-provider round-trip for pure local dev)

After step 5 (stack up), open `https://localhost:8443/health/live` in your browser (accept the self-signed cert warning), then F12 → Console, paste:

```js
(async () => {
  const r = await fetch('/dev/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'dev@app.local', groups: ['admin'] }),
  });
  const { access_token: t } = await r.json();
  sessionStorage.setItem('app-auth', JSON.stringify({
    state: {
      tokens: { accessToken: t, idToken: t, refreshToken: 'fake', expiresAt: Date.now() + 3600000 },
      user: { sub: 'dev', email: 'dev@app.local', name: 'Dev', identityProviders: [] },
      isAuthenticated: true,
    },
    version: 0,
  }));
  location.href = '/';
})();
```

The page reloads, RootRedirect sees `isAuthenticated=true`, lands on `/writing`. You're now in.

**4. Bring the stack up.**

```bash
cd upstream-framework
make up
```

Wait ~30-60s. Then sanity-check:

```bash
curl -sk https://localhost:8443/health/live   # → {"status":"ok"}
curl -sk https://localhost:8443/health/ready  # → may be 503/degraded in hybrid if no local reranker is wired
```

The 503 on `/health/ready` is intentional dev noise only when the
missing component is understood. In pure fake mode, `ARBITER_ENDPOINT_URL`
points at an unresolvable hostname (`arbiter.dev.fake`). In hybrid
source-upload mode, add the local arbiter service above; readiness may
still be degraded on `reranker`, but source indexing should reach
`upload_status=DONE`.

**5. Get a dev JWT and exercise the protected surface.**

```bash
TOKEN=$(curl -sk -X POST https://localhost:8443/dev/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"dev@app.local","groups":["admin"]}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')
echo "TOKEN=$TOKEN"

# Now hit any protected route
curl -sk -H "Authorization: Bearer $TOKEN" https://localhost:8443/api/conversations
curl -sk -H "Authorization: Bearer $TOKEN" https://localhost:8443/api/writing/projects
```

**6. Open in a browser**: `https://localhost:8443/` — accept the self-signed cert warning. The SPA's auth flow expects a real identity provider; since dev runs `AUTH_PROVIDER=fake`, the SPA login UI may bounce back to landing. The most reliable browser-side test is to skip the SPA login and pre-inject the dev JWT into sessionStorage via the DevTools console — same shape as the `app-auth` key the SPA uses against the cloud.

## The iteration loop

**Default decision rule:**

- UI/layout/form/nav bugs: use Vite HMR + local fake auth; do not deploy.
- Backend workflow/state-machine bugs: use local Postgres / vector store / API; add focused tests; do not deploy.
- Agent prompt/tool/LLM behavior bugs: use hybrid local-dev with your remote LLM provider; inspect local API logs and DB rows; deploy only after the local run proves the fix.
- Cloud-specific bugs (ingress/auth/secret-store/object-storage/managed-identity): use a cloud environment with cloud logs because those dependencies are the subject under test.

**Frontend changes (~1s feedback):**

For real hot-reload, run Vite's dev server alongside the Compose stack. It serves the SPA on a separate port with HMR (instead of using the prebuilt `dist/` via the reverse proxy).

```bash
cd upstream-framework/frontend
VITE_API_BASE=https://localhost:8443 \
VITE_AUTH_PROVIDER=fake \
  npm run dev -- --host --port 5173
```

Open `http://localhost:5173/` for HMR. Edits to `overlays/files/frontend/src/**` need to be rsynced again (`rsync -a overlays/files/frontend/ upstream-framework/frontend/`); Vite picks them up automatically once the file lands in `upstream-framework/frontend/src/`.

Better: install [`watchexec`](https://github.com/watchexec/watchexec) or use `inotifywait` to auto-rsync on overlay edits:

```bash
# Watch the overlay, mirror into the submodule on every save (so Vite HMR sees it)
watchexec --restart --watch overlays/files/frontend \
  'rsync -a overlays/files/frontend/ upstream-framework/frontend/'
```

**Backend changes (~3-5s feedback):**

The upstream api container does NOT mount source code by default — it builds the image from a Dockerfile. For hot-reload, add a volume mount and uvicorn `--reload`. The simplest path is editing `upstream-framework/deploy/dev.docker-compose.yml` to add:

```yaml
api:
  volumes:
    - ../backend/src:/opt/app/src:ro
  command: ["uvicorn", "src.server.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Then `make up` once; from then on, edits to `upstream-framework/backend/src/**` (rsynced from `overlays/files/backend/src/**`) cause uvicorn to reload in ~2s.

Without that, a backend change requires `make up` (rebuilds the api layer; ~20-40s warm).

**Inspecting state:**

```bash
# Postgres
PGPASSWORD=app-dev-password psql -h 127.0.0.1 -U app -d app -c \
  "SELECT workflow, COUNT(*) FROM llm_invocations GROUP BY workflow"

# Vector store
curl -s http://127.0.0.1:8081/v1/.well-known/ready

# Container logs (filter by emoji prefix)
docker compose -f deploy/docker-compose.yml -f deploy/dev.docker-compose.yml \
  --env-file deploy/.env logs -f api
```

## Teardown

```bash
cd upstream-framework
make down
# Destructive (drops postgres + vector-store volumes; only when you want fresh state):
make clean-dev
```

When done, also revert the dirty submodule working tree so the next cloud build isn't confused:

```bash
git -C upstream-framework checkout .
git -C upstream-framework clean -fd
```

## GOTCHA: local dist can be built for the wrong host

If your cloud frontend build writes to `upstream-framework/frontend/dist/` — the SAME path the reverse proxy bind-mounts as the local SPA — then running the cloud build (with a cloud env sourced) while your local stack is up makes the reverse proxy serve a cloud-targeted bundle to localhost. Symptoms: localhost tries to fetch `https://<cloud-host>/api/...`, the browser blocks it with CORS, and the home page shows "Couldn't load projects".

Fix: make cloud builds write their bundle to a separate path (e.g. `build/spa-dist/`) that the image build copies in, so they never clobber the local reverse proxy's `upstream-framework/frontend/dist/`.

**Recovery** (rebuild the local dist with the right env):

```bash
cd upstream-framework/frontend
VITE_AUTH_PROVIDER=oidc \
VITE_OIDC_TENANT_ID=<your-tenant-id> \
VITE_OIDC_CLIENT_ID=<your-client-id> \
VITE_API_URL=https://localhost:8443 \
VITE_API_BASE=https://localhost:8443 \
VITE_REDIRECT_URI=https://localhost:8443/callback \
VITE_SKIP_LANDING=true \
  npm run build
```

(Your identity provider's app registration must list `https://localhost:8443/callback` in its redirect URIs for the hosted sign-in to accept the local callback. If you target a different app registration, add it there too.)

**Prevention**: cloud builds should leave `upstream-framework/frontend/dist/` alone. If localhost starts calling a cloud host again, treat it as a regression in your cloud frontend build script or a stale local dist.

## Common gotchas

| Symptom | Cause / fix |
|---|---|
| `make up` fails with `docker-compose-plugin not installed` | Install Docker Compose v2: `sudo apt-get install docker-compose-plugin` |
| Port 8443 in use by a system service | `DEV_HTTPS_PORT=18443 make up` |
| `/dev/login` returns 404 | `DEV_FIXTURES_ENABLED` is not `true`. Defaults to true in `dev.env`; check your `deploy/.env` |
| SPA's `Sign In` button does nothing | Expected — `AUTH_PROVIDER=fake` short-circuits the real identity provider. Use `/dev/login` + DevTools to inject the JWT into sessionStorage under `app-auth` |
| Browser shows the old SPA after an edit | Vite HMR only fires on files inside `upstream-framework/frontend/`. Confirm your rsync landed (`ls -la upstream-framework/frontend/src/<the-file>`) |
| Container can't reach postgres | Wait ~30s for the postgres healthcheck. `docker compose ps` should show postgres `healthy` before api starts |

## When to NOT use this

- Testing anything that requires the real identity provider (the bounce-loop fix's actual exercise path).
- Testing cloud-specific infrastructure code (secret-store provider, object-storage ingestion, managed identity, gateway/load-balancer routing). These only run correctly in a cloud env.
- Running E2E against the same Postgres / vector store the cloud env uses — local has its own clean state.

Remote-LLM model behavior is the exception: it should be tested in hybrid local-dev when the code path can use a key/endpoint from local ignored env. For cloud-only infrastructure behavior, use a cloud environment and the browser + cloud-logs feedback loop.
