---
name: api
description: API mode — stress an app through the calls its clients make, with no browser. The API document (a flow map generated from the deployed code at lane start), the tools every lane shares, the tester as a model of the system, and the checks that find the most bugs per call — the reader table first, then the role matrix, out-of-order moves, races, refusal and audit checks, and the oracles (ground truth, export content, cost, liveness, logs). Use for API-only or API-first runs, contract, state, authorization and concurrency hunts, the late stages of a gated app, and agent swarms.
---

# API mode: stress the contract every client inherits

Why this mode works, what it cannot see and how it duels with the browser: [driving.md](driving.md). This file is how to do it. Running many testers at once on one environment: [lanes.md](lanes.md).

1. [The API document: the flow map](#1-the-api-document-the-flow-map)
2. [Tools, proven before the first call](#2-tools-proven-before-the-first-call)
3. [The tester is a model of the system](#3-the-tester-is-a-model-of-the-system)
4. [Flows and fixtures](#4-flows-and-fixtures)
5. [Checks, highest yield first](#5-checks-highest-yield-first)
6. [Oracles: one property across everything](#6-oracles-one-property-across-everything)
7. [Record and re-run](#7-record-and-re-run)

## 1. The API document: the flow map

Before the first call, get one document that answers: *which routes exist; who may call each; what each body needs; which routes change data, need a signature or start paid work; which call is refused until which other call happened; and which routes nobody has called.* This document is the **flow map**.

**Generate it at lane start from the deployed build. Never read a saved copy.** Rules, bodies and route contracts change between deploys. A map from an earlier run sends a lane to removed routes and old bodies. Verify each route and body against the router code at the deployed commit before you call it. On a fresh environment the runtime parts (the happy path from a real call log, the coverage) do not exist yet: generate the static map first with those sections marked pending, and regenerate it with the reliability gate's call log before handing out coverage slices.

**An OpenAPI page is the start, not the map.** When the server serves one, fetch it from the deployed build: it gives methods, paths and body and response schemas, but not who may call a route, the stage gates, the state machines, which steps are signed or paid, or which routes the app removes at boot. Those come from the router code at the deployed commit (a read-only checkout); the order of calls comes from the frontend's API client and one real call log of a complete flow. When the app serves no OpenAPI page, the route list *is* the code: grep the router decorators at the exact deployed commit.

Derive each section from the code's own owner of that fact:

| Section | Derive from |
|---------|-------------|
| **Stage graph** — the stages and what unlocks each | the server's gate table (the function the "is this stage open" read uses) and the frontend's nav-gating module |
| **State machines** — each multi-actor workflow (review, approval, lock) | the code's table of legal moves and of each move's requirements, with the refusal code per requirement |
| **Route table per stage** — method, path, required capability, mutating?, signed?, starts a paid run? | the router decorators and their access dependencies; the mount list (drop routes the app removes) |
| **Frontend call order per page** — calls on load and on each main action | the frontend's API client and the hooks that call it; say what static extraction could not resolve rather than inventing calls |
| **Happy path as an ordered call list** | the frontend order plus a real call log of one complete flow |
| **Dependency edges** — "B is refused until A", with B's refusal code | the gates above; one small graph per stage, not one giant graph |
| **Coverage overlay** — per route (and per action, for a route that takes an action field): which lanes called it, which statuses were seen | the lanes' call logs, with ids in paths normalised |

Keep hand-written input to one small overlay file for facts the code cannot give (which runs cost money, typical durations), each with its reason. **No silent drop:** every route the code declares is a row of the table or carries a reason why not; an unexplained declaration fails the generator, because a route missing from the map is a route no lane will test.

**Each API lane generates its own map, with a receipt.** The code alone gives no coverage, so every lane brief gives the map command and its inputs: the checkout, the target environment, the full commit actually serving it (not a branch tip), the campaign's call logs and saved server request-log windows **for that environment and build only**, and a new directory for this lane. Evidence from an older build never counts toward the current coverage: a route the deploy changed is not covered by an old success. Report older coverage apart, if at all. A sketch, with the project's generator in place of `flow-map`:

```bash
map_dir="$LANE_DIR/map-$(date -u +%Y%m%dT%H%M%S.%NZ)"; inputs="$map_dir.inputs.txt"
logs="$SERVER_LOG_DIR/$TARGET_ENV-$DEPLOYED_SHA"
test ! -e "$map_dir" || { echo "❌ refusing to reuse an existing flow-map directory: $map_dir" >&2; exit 1; }
{ printf 'env %s ref %s\n' "$TARGET_ENV" "$DEPLOYED_SHA" &&
  { test ! -d "$RUN_ROOT/lanes" || find "$RUN_ROOT/lanes" -type f -name "calls-$TARGET_ENV-$DEPLOYED_SHA.log" -printf 'calls %p\n'; } &&
  { test ! -d "$logs" || find "$logs" -type f -name '*.log' -printf 'server-log %p\n'; }
} > "$inputs" || { echo "❌ could not list the map inputs" >&2; exit 1; }
map_args=()
while read -r kind path; do map_args+=("--$kind" "$path"); done < <(tail -n +2 "$inputs")
flow-map --ref "$DEPLOYED_SHA" "${map_args[@]}" --out "$map_dir" \
  || { echo "❌ flow-map failed for ref=$DEPLOYED_SHA; no receipt" >&2; exit 1; }
printf '🗺️ flow-map env=%s ref=%s out=%s inputs=%s\n' "$TARGET_ENV" "$DEPLOYED_SHA" "$map_dir" "$inputs"
```

No saved windows or call logs for this build yet (a fresh environment) is not an error: the map is static and its coverage pending. A listing that fails on evidence that does exist is an error. Every generation — the static map, the regeneration after the gate, a map for a new build — gets its own directory and receipt; an existing map directory is a stop condition, never a shortcut: never write to a shared default output or copy a map from an earlier lane. The lane report keeps the final receipt line and the input list beside it: the environment, the exact full commit (a shortened label inside the map is evidence only beside it) and every file the map was built from. Save the server's request log in fixed UTC windows that start after the build began serving, filed under that environment and build, and when the log tool truncates a window (many keep only the newest few hundred lines), split it into non-overlapping windows and pass each as its own input. Keep these receipts with the report, and never claim coverage from a call file the command did not include.

The coverage overlay turns the map into a work list: **routes no lane has called with an authenticated, well-formed request**, and **mutating routes never seen to succeed**. Hand each lane the map and its slice of that list; hand the next wave whatever is still on it. For a route that takes an action field (a transition route that takes `submit`, `approve`, `reject`), log the action in the call log and count coverage per action: **actions never tried** belong on the work list too, or coverage counts the route and hides them. This work list is the one coverage definition; lane briefs and the next wave point here. Diff the maps of two commits or two environments to get the gates and routes that changed — the first place to look after a release.

Render the graphs in a text format that lives next to the code (Mermaid in Markdown), keep the long tables in a machine-readable file beside it, and give every statement its source (file and line, overlay entry, or call log). The map also feeds the cheapest mischief there is: a walker that takes random legal and illegal steps along the edges and checks after each one that the state read still agrees with the map.

## 2. Tools, proven before the first call

A lane that discovers a broken helper wastes its whole budget: a lane whose client fails to import can spend its whole time box making a handful of calls. Build and **run** each tool before any lane starts. Keep the tools, the flow-map generator and the check pack ([§7](#7-record-and-re-run)) in the project itself, next to the code they read (a project skill or a scripts folder), so every lane and every session uses the same ones.

| Tool | Why |
|------|-----|
| **Client** — one function: user, method, path, body → status, body. Never raises on an HTTP status. Writes one call log per environment and build (`calls-<env>-<commit>.log`, so coverage can tell builds apart) with method, path, status, elapsed time, the actor (anonymous, role, administrator), a test-case id and whether the request was malformed on purpose; never a token or a body with private text. | Every lane asserts on refusals; a client that throws on 4xx hides the data. The call log is the coverage record and the repro. |
| **Token source, one per role** — per-user file, refreshed under a per-user lock, expiry checked before each call. Prefer a grant that needs no browser for throwaway test accounts (try the identity provider's token endpoint before scripting its sign-in page); keep a scripted sign-in only for steps that truly need it, such as a re-authentication bound to a challenge. | One script acts as every role of the team in the same minute. Lanes run longer than a token lives; two lanes minting one user at once break each other. |
| **Signed-step helper** — whatever a re-authenticated or confirmed step needs (a challenge, a fresh sign-in, an attestation id). Hold one lock per signer from the challenge to the signed call: a second challenge for the same signer can replace the first. | The most valuable late-stage tests need it; each lane re-deriving it is hours lost. |
| **Never-call filter, inside the client** — whole-dataset exports, account deletion, inbound webhooks, bulk imports, anything that changes a real third-party connection. | A sweep that iterates the route map would otherwise call them; it must drop them by path before its first call. |
| **Logs helper** — one command that reads the server and worker logs of the target environment, filtered by a request, run or object id. | The second layer for every finding ([§6](#log-cross-check)). |
| **Code tree at the deployed commit**, read-only. | Route list, bodies, and the code pointer every issue needs. |

**One pacing gate for the whole box.** A gateway or WAF rate limit is per client IP, and every lane on one machine shares that IP; ten lanes that each pace themselves politely still add up to a burst. Put the gate in the shared client: one lock file, a minimum interval between any two calls box-wide, and an explicit opt-out for a deliberate race of a few calls. Find the real limit in the infrastructure code before choosing the interval.

**Never retry a slow or timed-out call blindly.** A wrapper that re-sends on a client timeout turns one heavy request into several concurrent ones; the server keeps working on each after the client has left. One lane's retry of an unbounded export took a whole environment down this way — a real finding, and also an outage for every other lane. Catch the timeout, report it, read the logs, and decide. Mark the routes that read *everything* as call-once.

**Learn the gateway's signature.** A refusal from the gateway is not an app finding *when the lanes caused it* (throttling): learn its shape (an HTML body, the gateway's name in it) and tell every lane. A gateway that blocks a legitimate request from a supported client or a normal user action is an infrastructure finding: file it with the request and the rule that fired. Expect it to refuse a default HTTP-library agent string too: if a plain `curl` gets 200 and your script gets 403, compare the headers before suspecting the app.

## 3. The tester is a model of the system

Each HTTP call is stateless: it carries its own token and the API process keeps no session. The **system** is not: rows in the database, stored files, a search index, queued background runs, leases and an audit trail all persist between calls. So an API tester is a small state machine of its own. It holds a model of the object ("round 4, in write, I hold the lease, the form is locked"), predicts the answer to the next call from that model, and after the call compares three things:

1. the **response** against the prediction (status, error code, the fields that matter);
2. the **server's own state read** (the state route, the audit records) against the model;
3. the model itself, updated only by calls that succeeded.

Model the answer to a call that starts background work as *accepted → pending → done / failed*, not as done: compare the state read only after the route's documented completion point, and call it a finding when it never arrives or arrives wrong. Every disagreement that survives that is a finding, and which pair disagrees says where to look: response vs model is a wrong rule or a wrong doc; two of the server's own reads disagreeing with each other is one fact with two owners ([§5.1](#51-the-reader-table-one-fact-every-reader-every-role)); a correct response that left the stored state unchanged (or changed it twice) is an atomicity or idempotency defect (a job that reports `succeeded` beside unchanged stored state is the plain case; an expected no-op must say so). Remember two states the model does not see by default: the **API process's hidden state** (in-flight work, single-use tickets, caches, memory) — only repetition, concurrency and long requests reach it — and the **browser's copy** of the state, which no API run reads at all.

The flow map is this model written down once for everyone, instead of living in each lane's head.

## 4. Flows and fixtures

### A simulated flow

A **simulated flow** is the user's path written as the calls the frontend really makes, in the frontend's order — not the calls you think the backend should accept.

1. Read the frontend's API client to learn the calls and their order; read the router for each body. The frontend is the truth for *what a user's session sends*; the router is the truth for *what the server does*, not for *what should be legal* — take intended rules from the product docs or requirements, and report every place the code and the intent disagree (a missing gate is invisible if the code is also your oracle).
2. Write one resumable driver per flow: every step records its ids and timestamps in a state file, so a crashed or replaced worker continues instead of starting again. For a mutating step, write the intent to the state file **before** sending, use the API's idempotency key where it has one, and after a crash read the server's state to learn whether the step happened before replaying it — a checkpoint written after the call cannot tell a lost reply from a lost request, and a replayed paid run or signature is a second effect.

### Stand on what exists

Do not pay, in time or in metered work (paid runs, model calls), to rebuild upstream state for every lane. A late stage of a gated app can sit hours of upstream work (forms, paid runs, approvals) away from a fresh object. A lane that builds its own late-stage object can spend its whole time box on setup and reach none of its checks; a lane that reuses a prepared object already at that stage runs its whole matrix.

- **Mark test data as test data.** Prefer idempotent or clearly prefixed throwaway resources (`STRESS-…`, `COMB-…`, `MISCHIEF-…`), so a later tester can tell them from real data, and clean up what you created.
- **Survey first.** List every object in the environment with its stage, owner and age. The ones earlier runs left at late stages are your seeds.
- **One exclusive object per lane**, claimed in a shared file before the first write. Two lanes on one object produce false alarms that look exactly like races.
- **Write the protected list down.** Client data, demo data, another team's acceptance fixtures: named, in the brief, read-only.
- **An old fixture is not a current fixture.** Rules tighten between releases. A step that looks reversible on a seed (reopen a form, unlock a stage) can be a one-way door when the object was made under older rules: the way back now demands work the fixture never did. Before a destructive step on a seed, check the way back with a read (the readiness or validation answer), or do the reversible-cycle tests on a fresh object. When a fixture does strand, that is a finding too: the same door is open to real users with old data.
- **One fresh end-to-end flow still runs** as the reliability gate ([reliability.md](reliability.md#the-gate)).

## 5. Checks, highest yield first

### 5.1 The reader table: one fact, every reader, every role

The most serious bugs an API campaign finds are one fact decided in two or more places that drifted apart: who acts next, what blocks the next step, is it complete, has it been read, how many items are open. In one API-only campaign about a third of the medium-or-worse findings were readers of one fact that disagreed, and one such fact had been fixed several times before, each time in the one reader that happened to look wrong.

1. **Pick a fact a person acts on.** Who acts next; what blocks the next step; is it done or ready; how many open items; may I do this.
2. **List every reader of it** the API exposes: the status line or summary sentence; the "waiting for" list; the actions list with each action's allowed flag and reason; the action route itself (call it — its refusal is the reader that decides); the list row's own status column; a count against the list it counts; readiness reads (can-lock, export readiness, a gap list); notifications; the activity history; the exported document.
3. **Put the system in one state, preferably an edge.** Readers part at edges: just after a role change, an item answered but not closed, a reopen, a second approver, an archived or unlinked object, a check reused because nothing changed.
4. **Ask every reader, as every role and as a non-member, in the same minute.** The API makes this cheap: one script, one token per role, a few dozen calls.
5. **Write the table:** reader · called as · what it said. Two rows that disagree for the same input are a finding. So is a next action that every reader agrees on but that does not exist, or that the actor it names cannot take: call it as that actor.
6. **File the first disagreement; never wait for a second.** Class `one-fact-many-owners`: put the table in the finding (its issue or artifact entry, [findings.md](findings.md)), list every reader you reached and the earlier issues of the same fact. The fix is one owner that every reader renders, not a patch to the reader that looked wrong ([findings.md](findings.md#fix-the-issue-behind-the-issue)). If the `deslop` skill is installed, its pattern *one fact, many owners* names the repair.

A synthetic example of the shape such a table takes (an approval request, one fact: who acts next):

| Reader | Called as | What it said |
|---|---|---|
| state: status line | author | "Revise the request and resubmit it." (author acts) |
| state: allowed actions | author | only `withdraw` allowed (author acts) |
| state: waiting for | author | the approver (approver acts) |
| state: status line | approver | "The author must withdraw and revise…" (author acts) |
| revise route, called | author | 423 `request_locked`: withdraw first (author acts; lowercase code) |
| attachment upload, called | author | 423 `REQUEST_LOCKED` (the same refusal, another spelling) |

The same table catches these variants:

- **Count parity.** For every list that carries a count, fetch both and compare over all rows: a total against the walked list, a roles count against the member list, a list row's fields against the detail read of the same row (a field such as a cost that is null on the detail and set on the list is this class), an "N open" sentence against the lists it summarizes. A row that is listed but whose detail read refuses is a third kind: listed but not openable.
- **After every upstream change.** After each upstream unlock, edit and re-lock, read every view of readiness (the workflow state, the stage's own read, the refusal text of each downstream move) and require them to agree and to name a reachable next action.
- **After a replace.** After replacing a source file, read every reader that cites it (source lists, stale flags, evidence search, citations, consistency checks) and judge each against its documented replacement policy. A reader of the current source must not return the old version except as an explicit "replaced" notice; a version-pinned artifact (a signed report) citing the version it was made from is correct provenance. With no replaced data present the check sees nothing, so make one.
- **A reader with no read route.** When a fact reaches people only as a push (a notification feed with no GET), no table can include it, and its disagreements stay invisible. Observe the delivered event where you can; otherwise record the reader as untestable in the report, and file the missing read route — as a defect when the product promises a way to read the fact again, otherwise as a testability request.
- **The page's copy.** The browser shows a fact the API also states; a page that shows something else has re-decided the producer's fact. That row is a browser lane's twin check ([driving.md](driving.md#how-to-duel-them)).

### 5.2 The role matrix

A browser pass yields anecdotes. An API pass should yield a table that someone can re-run:

| Axis | Values |
|------|--------|
| Move / route | every transition and every mutating route of the stage |
| State | every state the stage can be in |
| Actor | each role, a signed-in non-member, a removed member, a disabled account (its token may still be valid), a member of another object using that object's ids, an administrator who holds no role on the object, anonymous |
| Condition | each precondition made false in turn |

For each cell: expected (from the docs or the code's own table of legal moves) → actual (status, error code, the audit record). Legal cells succeed **exactly once**; illegal cells are refused with the documented code, write the documented refusal record, and never answer 5xx. "What held" is part of the report — it is the coverage record that makes the next run cheaper.

- **Every route that takes an object id**, reads and downloads included, gets the anonymous, non-member and wrong-role calls, not only the mutating routes of the stage.
- **Authorization comes first in the refusal order.** The documented authorization refusal (often 403; some APIs answer 404 on purpose to hide existence) arrives before any validation, state or lock refusal; a body names the state when the state is the cause; and never are two roles each told the other must act. Send an empty or bogus body to mutating routes so nothing real changes when a gate is missing.
- **No existence oracle.** A non-member asking for a real object and for a nonexistent id gets the same refusal body.
- **Isolation.** As a non-member of object A, call every list, search, feed, export, activity and notification route, scoped to A's ids and unscoped, and search the responses for A's private strings (titles, file names, comments, counts). Run the same calls as a member first: the positive control proves the strings would show. Then send another object's child ids inside your own object's routes and bodies (cross-object ids): each must be refused, never accepted or re-parented.
- **Capability against controls.** Diff the route table's declared capability against what the membership read says the role holds and against the controls the UI shows for that role: a control with no capability is a bug, and so is a capability with no control (a dead end).
- **Frozen means frozen.** In every state where content must not change, try every writer (text, attachments, upstream locks, settings). A write that succeeds is the most serious thing an API run can find.
- **Administrators prove nothing for authorization.** Test the matrix with ordinary roles; an administrator on the roster acts in that role for workflow mechanics only.

### 5.3 Out-of-order moves

The UI offers only the moves it thinks are legal, in the order its pages lead. The API lets you make the rest:

- **Next stage early.** Before each stage opens, call the **next** stage's main route once and record the refusal — after the reliability gate, on the lane's own object, never on the gate's fixture. A gate that lets you through early is a finding; a gate that refuses with the wrong reason is one too.
- **Illegal transitions.** Skip a step, call a later route first, reuse an id after delete, replay a create.
- **Downstream while upstream is open.** Unlock an upstream stage, then call each downstream sign, lock or start: the refusal must be the one the read route states, and no start route may bypass it — call every route that starts the same work (the census of those routes: [bug-hunter.md](bug-hunter.md), class 7).
- **A warning the next step accepts.** For every stage that reports problems (conflicts, readiness blockers), read the problem list, then call the next step with the problem standing. It must be unambiguous which problems block (a severity, separate collections or a blocking flag all pass), and the next route's acceptance must match that and the documented gate — two routes that agree with each other but not with the documented gate are still a finding.
- **The order of refusals.** When several preconditions fail, the refusal must name the first one the docs name; a wrong order sends the user to fix the wrong thing.
- **A change of mind.** Go back, change an answer, re-pick, unlock and re-lock with nothing changed. Nothing may go stale, reopen or start paid work unless content changed, and nothing signed may change silently.
- **Mid-flight.** Start a background job, then cancel it, retry it, or change its inputs while it runs. Expect one run, a clean cancel with no half-written output, or a refusal or a new run that says why; never a stuck or duplicated run.
- **Ceremony abuse.** For signed or confirmed steps: replay a spent challenge, use one issued for another action, user or object, let it expire, send an ordinary session token in its place. Nothing is signed by a refused call: read back the signatures and the audit records.

### 5.4 Races

Two to ten threads on one transition, from different people where it makes sense, each race repeated about five times (report "N of M": races are intermittent). Keep each burst at ten calls or fewer.

- **Exactly one effect.** One winner, one transition record; losers get the refusal the route's contract documents (usually a clean conflict that names who won). A transition that is idempotent by design, or retries that share one idempotency key, may return success to every caller: assert the count of effects and records, not that every reply differs.
- **Double-submit.** Send each create or submit twice in a row with the same idempotency key, then twice with none: duplicate rows, double charges, a second paid run.
- **Two writers, one record.** Send every write route twice at once (same body, then two users with different bodies) and once with a stale version token. Expect a read-back showing one body in full. Where a 200 carries a success boolean (`released`, `ok`), force the false path and demand a reason. Two owners claiming one exclusive resource (a folder, a lease, a unique name): exactly one is accepted ([exactly one effect](#54-races)), and the loser is refused by the claim itself — not later, by a background run — with the documented refusal, naming the holder where the contract says so.
- **Time of check vs time of use.** When a code reader says "the role is read at the request edge and the write happens seconds later under a lock", script the change in between ([lanes.md](lanes.md#the-hypothesis-loop-code-reader-to-live-lane)).
- **A race is a finding** when the end state is impossible by the rules: two winners, a move applied on a stale state, a lost write behind a 200, counts that never agree again, a lease held by two, an audit record missing or doubled, a 500, or a state no move can leave.

### 5.5 Refusals and audit

- **The refusal sweep.** Collect the 4xx body of every route (empty body, wrong type, wrong role, unknown id, wrong state). Assert one envelope (a code and a message), a message that is not the code, that names what is missing, who can fix it and the next action, and a field name on validation errors ("String should have at most 500 characters" with no field is a miss). The same fact carries the same code everywhere (lease held, stage frozen, not linked, stale version), and every code is one the frontend can show (grep the frontend for it). No stack trace, raw SQL or constraint name. Fixing the client to avoid a refusal does not close the class: rerun the sweep after each such fix.
- **A refused action leaves the audit record its policy documents.** After each authorization or domain refusal of an audited action (a wrong role, a non-member, an anonymous caller, a forbidden state), read the scoped audit trail (never a whole-trail export) and require the documented refusal record with actor, action and outcome — the same expectation as the role matrix. Where the policy is silent, a refusal that leaves no trace of who tried what is a finding to raise; a malformed request rejected before any action may write nothing if that is the contract.
- **An empty result matches its contract** (for example `200` with an empty list, plus any reason field the contract promises), never a 500.

### 5.6 Input and hygiene

- **Typed-input fuzz per route.** For each route that takes an id, enum, free text or typed answer, send: a well-formed id that does not exist, to every route taking that id kind (all must answer in the same status class, never 200 with invented data); the wrong JSON type; a value outside the option list; gateway-sensitive text (`>=`, `; select`, quoted phrases, `<script>`); 501 and 20 000 characters (a gateway may answer an HTML error above its URL limit); a null byte; leading and trailing whitespace, zero-width and right-to-left characters. Read back: what was stored equals what was sent or its one canonical form, derived counters agree with the stored values, and a refused input queued no paid job. A value checked on a cleaned copy but stored raw is the class *validated, not parsed*.
- **Contradictory fields.** Fields that are each valid alone but impossible together (an end before its start, a child id from another parent, a status that disagrees with a flag): a cross-field invariant the server must refuse.
- **Payload matrix.** The same route with many *valid* variants (optional fields, empty strings, unicode, large bodies, boundary ids): 500s on weird-but-legal input.
- **Contract drift.** Compare each response's shape with the OpenAPI document and with what the frontend client reads: renamed fields, null vs missing, pagination surprises.
- **Stale credentials.** An expired or revoked token, the wrong `Authorization` scheme, a cookie-only route without its CSRF guard.
- **API hygiene sweep.** Malformed JSON, oversize bodies, wrong method, unknown path, CORS from a foreign origin, security headers, error bodies that leak.

## 6. Oracles: one property across everything

A driving check walks one path and finds what breaks on it. An **oracle** checks one property across everything the system does, and finds a *class*. Most oracles are read-only and cheap, so run them beside the driving lanes, not after them.

| Oracle | The property | How to run it | What it finds |
|---|---|---|---|
| **Consistency** | Every reader of a fact agrees, and agrees with what the action does | The reader table ([§5.1](#51-the-reader-table-one-fact-every-reader-every-role)) for each fact a person acts on | A status line that names the editor while the route needs a reviewer; `allowed: true` and a refusal; a blocker that names a move that does not exist |
| **Cost** | No paid work repeats a finished result for the same inputs unless a person explicitly asked for it | Do the everyday actions (save unchanged, unlock and re-lock, re-submit, send and return, re-pick) and record every paid run each starts; a retry after a failure, or an explicit request to generate again, is not a finding | Re-runs decided by an event or a time instead of the inputs; one click that starts two runs |
| **Liveness** | Every running or waiting state moves within a bound, or names who it waits for | Every few minutes for an hour or two, list queued, running and cancelling work and every waiting state from one system-wide list of active work (sampling each object's newest run hides an older stalled run behind it); read the run history with its timestamps for bounds broken between samples | Silent stalls; cancels that never finish; work queued behind nothing; a terminal row with no reason; an active-run flag that disagrees with the live job |
| **Log census** | Every distinct error and warning class has an owner | Pull a day or two of error and warning lines, cluster them by site and cause, and match each class to an open issue | Failures nobody filed because each looked like noise; counts that show which class costs most |
| **Run census** | Every failed or cancelled background run has a named cause | List the failed and cancelled runs of a period, group by kind and cause | Unclassified failures; a cancel reason that is not what happened; one cause behind many kinds |
| **Ground truth** | A generator's output covers what a known-good output covers, faithfully | Where real finished examples exist, read them first, then compare the generated output by section — length, and each key fact present, missing, wrong or unsupported; where the output cites a source, check that the cited passage states the value | Systematic gaps by class (a table never filled, a fact always missed); a wrong value with a confident citation |
| **Record** | What is delivered is exactly what was approved | Where the product delivers what was approved: export after an approval, download the package and inspect its **content**, not only its status: each document's content and version identity against the approved version (the version the approval bound, not the newest), after only the transformations the product declares; every file against its manifest entry; the signatures listed against the approval; then export twice and diff, allowing only the parts the product declares variable (timestamps, provenance, signature material), and require byte equality only where the product promises it | Unapproved text in a delivery; a manifest that does not match its files; a second export whose content differs |

Rules:

- **Write the property down first**, in one sentence, before the lane looks at anything. A lane that starts browsing for problems becomes a comb pass.
- **A finding is a class.** Report the property, every instance found, and the one place that should own the fact. Twelve instances of one class are one issue with twelve rows.
- **The oracle needs a ground.** Consistency needs the route's real answer, cost needs the run list, ground truth needs a known-good output. If the ground is missing, say so and stop; do not guess it.
- **Check the ground before you report.** A surprising result is often a wrong ground: the newest version instead of the approved one, test data an earlier lane wrote ([findings.md](findings.md#what-counts-as-a-real-finding)), or a tool that silently defaults to another environment (print the target before every conclusion; "everything vanished" usually means you asked the wrong place).
- **A read can write.** On audited systems, downloads and some reads append audit records. Name those effects in the lane's brief instead of calling it read-only, and ask the environment's owner only when the reads go beyond what the brief already authorizes.

### Log cross-check

A response shows what the client was told; the logs show what the server and its workers did. After every surprising answer and every paid run, read the logs for that request, run or object id. An error line for your object is a finding even when the response looked fine, and a run that answered 202 has not happened until its worker logs say so. Reading the environment's logs across all lanes is the coordinator's job ([lanes.md](lanes.md#the-coordinator-reads-the-logs)).

## 7. Record and re-run

- **A repro is a call list:** method, path, headers (secrets redacted), body, expected vs actual, and the call number in the lane's call log. It travels better than "I clicked around", and anyone can run it again.
- **Turn finished checks into a re-runnable check pack.** One row per rule, each with a result: PASS; FAIL; KNOWN (it fails exactly as a filed issue says: the issue and the exact actual value); NOT_JUDGED (the pack did not or could not test it, with the reason); ERROR (the run is incomplete there: a deploy window, a timeout, a gateway page). NOT_JUDGED and ERROR are never a pass. When a KNOWN row starts to pass, its issue is fixed; remove the mark.
- **Sweep hygiene.** Time-ordered ids share a long common prefix, so never key sweep results by a short prefix. A 503 "updating" mid-sweep voids the probes it touched: retry them with a deadline before concluding anything from them, and keep the findings that were confirmed independently. A route that "exists but returns empty" may need a query parameter (search routes): read the route code before calling it a gap.
