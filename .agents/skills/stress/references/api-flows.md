---
name: api-flows
description: API-first stress runs — simulate a user flow with the calls the frontend makes, root out logic and workflow bugs without a browser, and run many lanes in parallel on one deployed environment. Use when the late stages of a gated app are under-tested, when the box cannot afford many browsers, or when the user asks for API-only or simulated-flow stress.
---

# API flows: stress the logic without the browser

A browser session costs gigabytes of memory and minutes per step. A scripted HTTP flow costs nothing on the box and runs a step in a second. For a **gated, multi-stage app** this changes what you can test: the late stages (review, approval, signature, lock, export) sit behind hours of upstream work in the UI, so browser runs reach them last and least. By API you can stand on a project that is already there and attack that stage alone, in every order, as every role.

This file is the playbook for that. It does **not** replace the front door: [driving.md](driving.md) still holds — what renders is the product, and an API run sees none of it. Use this for the class the browser is slow or blind at: **state machines, role rules, ordering, concurrency, idempotency, signatures, audit records, data integrity.**

## What an API flow is

A **simulated flow** is the user's path written as the calls the frontend really makes, in the frontend's order — not the calls you think the backend should accept.

1. Read the frontend's API client to learn the calls and their order; read the router for each body. The frontend is the truth for *what a user's session sends*; the router is the truth for *what is legal*.
2. Write one resumable driver per flow: every step records its ids and timestamps in a state file, so a crashed or replaced worker continues instead of starting again.
3. Log each call as method, path, status and elapsed time. No tokens, no bodies with private text.
4. Before each stage opens, call the **next** stage's main route once and record the refusal. A gate that lets you through early is a finding; a gate that refuses with the wrong reason is one too.

**Verify every endpoint against the code at the deployed commit before you call it.** Drivers from an earlier run drift; lock and signature payloads drift most. If the deployed app serves no API description page, the route list *is* the code: grep the router decorators in a read-only tree checked out at the exact deployed commit.

## The tester is a model of the system

Each HTTP call is stateless: it carries its own token and the API process keeps no session. The **system** is not: rows in the database, stored files, a search index, queued background runs, leases and an audit trail all persist between calls. So an API tester is a small state machine of its own. It holds a model of the object ("round 4, in write, I hold the lease, the form is locked"), predicts the answer to the next call from that model, and after the call compares three things:

1. the **response** against the prediction (status, error code, the fields that matter);
2. the **server's own state read** (the state route, the audit records) against the model;
3. the model itself, updated only by calls that succeeded.

Every disagreement is a finding, and which pair disagrees says where to look: response vs model is a wrong rule or a wrong doc; two of the server's own reads disagreeing with each other is one fact with two owners; a correct response that left the stored state unchanged (or changed it twice) is an atomicity or idempotency defect. Remember two states the model does not see by default: the **API process's hidden state** (in-flight work, single-use tickets, caches, memory) — only repetition, concurrency and long requests reach it — and the **browser's copy** of the state, which no API run reads at all.

The flow map of Step 0 is this model written down once for everyone, instead of living in each lane's head.

## Step 0 — build the flow map (generated, never hand-kept)

Before the first lane starts, build one artifact that answers: *what are the user flows, which calls does the frontend make in which order, which call is refused until which other call happened, and which routes has nobody exercised?* A hand-written map is stale in a week, so **generate it from the code at the deployed commit** and regenerate it at the start of every run. Keep hand-written input to one small overlay file for facts the code cannot give (which runs cost money, typical durations), each with its reason.

Derive each section from the code's own owner of that fact:

| Section | Derive from |
|---------|-------------|
| **Stage graph** — the stages and what unlocks each | the server's gate table (the function the "is this stage open" read uses) and the frontend's nav-gating module |
| **State machines** — each multi-actor workflow (review, approval, lock) | the code's table of legal moves and of each move's requirements, with the refusal code per requirement |
| **Route table per stage** — method, path, required capability, mutating?, signed?, starts a paid run? | the router decorators and their access dependencies; the mount list (drop routes the app removes) |
| **Frontend call order per page** — calls on load and on each main action | the frontend's API client and the hooks that call it; say what static extraction could not resolve rather than inventing calls |
| **Happy path as an ordered call list** | the frontend order plus a real call log of one complete flow |
| **Dependency edges** — "B is refused until A", with B's refusal code | the gates above; one small graph per stage, not one giant graph |
| **Coverage overlay** — per route: which lanes called it, which statuses were seen | the lanes' call logs, with ids in paths normalised |

The overlay turns the map into a work list: **"routes no lane has called with an authenticated, well-formed request"** and **"mutating routes never seen to succeed"**. Hand each lane the map and its slice of that list; hand the next wave whatever is still on it. Diff the map of two environments or two commits and you get the list of gates and routes that changed — the first place to look after a release.

Render the graphs in a text format that lives next to the code (Mermaid in Markdown), keep the long tables in a machine-readable file beside it, and have every statement carry its source (file and line, overlay entry, or call log). The map also feeds the cheapest mischief there is: a walker that takes random legal and illegal steps along the edges and checks after each one that the state read still agrees with the map.

## The matrix is the deliverable

A browser pass yields anecdotes. An API pass should yield a table that someone can re-run:

| Axis | Values |
|------|--------|
| Move / route | every transition and every mutating route of the stage |
| State | every state the stage can be in |
| Actor | each role, a signed-in non-member, an administrator who holds no role on the object, anonymous |
| Condition | each precondition made false in turn |

For each cell: expected (from the docs or the code's own table of legal moves) → actual (status, error code, the audit record). Legal cells succeed **exactly once**; illegal cells are refused with the documented code, write the documented refusal record, and never answer 5xx. "What held" is part of the report — it is the coverage record that makes the next run cheaper.

High-yield additions once the matrix exists:

- **Frozen means frozen.** In every state where content must not change, try every writer (text, attachments, upstream locks, settings). A write that succeeds is the most serious thing an API run can find.
- **The order of refusals.** When several preconditions fail, the refusal must name the first one the docs name. A wrong order sends the user to fix the wrong thing.
- **Ceremony abuse.** For signed or confirmed steps: replay a spent challenge, use one issued for another action, another user, another object; let it expire; send an ordinary session token in its place.
- **Races, small and deliberate.** Two to ten threads on one transition: exactly one wins, one record is written, the loser gets a clean conflict.
- **Time of check vs time of use.** When a code reader says "the role is read at the request edge and the write happens seconds later under a lock", script the change in between (see the hypothesis loop below).

## Stand on what exists

Do not pay (in time or in model spend) to rebuild upstream state for every lane.

- **Survey first.** List every project/tenant/object in the environment with its stage, owner and age. The ones that earlier runs left at late stages are your seeds.
- **One exclusive object per lane.** Two lanes on one project produce false alarms that look exactly like races.
- **Write the protected list down.** Client data, demo data, another team's acceptance fixtures: named, in the brief, read-only.
- **An old fixture is not a current fixture.** Rules tighten between releases. A step that looks reversible on a seeded object (reopen a form, unlock a stage) can be a one-way door when the object was made under older rules: the way back now demands work the fixture never did. Before a destructive step on a seed, check the way back with a read (the readiness or validation answer) — or do the reversible-cycle tests on a fresh object. When a fixture does strand, that is a finding too: the same door is open to real users with old data.
- **One fresh end-to-end flow still runs** as the reliability gate ([reliability.md](reliability.md)), in parallel with the lanes that stand on seeds. Measure each stage's wall-clock; a stage that takes hours by API is its own finding.

## Shared tools, proven before any lane starts

A lane that discovers a broken helper wastes its whole budget. The coordinator builds and **runs** each of these first:

| Tool | Why |
|------|-----|
| **Client** — one function: user, method, path, body → status, body. Never raises on an HTTP status. | Every lane asserts on refusals; a client that throws on 4xx hides the data. |
| **Token source** — per-user file, refreshed under a per-user lock, expiry checked before each call. Prefer a grant that needs no browser at all for throwaway test accounts (try the identity provider's token endpoint before scripting its sign-in page); keep the scripted sign-in only for steps that truly need it, such as a re-authentication bound to a challenge. | Lanes run longer than a token lives; two lanes minting one user at once break each other; a browser per token refresh is the last browser an API run should need. |
| **Signed-step helper** — whatever the app needs for a re-authenticated or confirmed step. | The most valuable late-stage tests need it; each lane re-deriving it is hours lost. |
| **Logs helper** — one command that reads the server and worker logs of the target environment. | The second layer for every finding (see [findings.md](findings.md)). |
| **Code tree at the deployed commit**, read-only. | Route list, bodies, and the code pointer every issue needs. |

### One pacing gate for the whole box

A gateway or WAF rate limit is **per client IP**, and every lane on one machine shares that IP. Ten lanes that each pace themselves politely still add up to a burst. Put the gate in the shared client: one lock file, a minimum interval between any two calls box-wide, and an explicit opt-out flag for a deliberate race of a few calls. Find the real limit in the infrastructure code before choosing the interval.

**Never retry a slow or timed-out call blindly.** A wrapper that re-sends on a client timeout turns one heavy request into several concurrent ones; the server keeps working on each after the client has left. One lane's retry of an unbounded export took a whole environment down this way — a real finding, and also an outage for every other lane. Catch the timeout, report it, read the server's logs, and decide. Mark the routes that read *everything* as call-once.

A refusal from the gateway is not an app finding — learn its signature (an HTML body, the gateway's name in it) and tell every lane. Also expect the gateway to refuse a default HTTP-library agent string outright: if a plain `curl` gets 200 and your script gets 403, compare the headers before suspecting the app.

## Lanes

Split by **part of the app**, not by mode: each lane owns one stage or one cross-cutting concern and runs comb *and* mischief on it. A split that worked for a gated authoring app (adapt the names):

- one lane per late stage (review/approval machine · drafting and run control · lock/export/deliverable content);
- one fresh end-to-end flow (the reliability gate);
- one lane for objects, membership, roles, leases — it also owns the **authorization matrix of the whole API** (every route that takes an object id × anonymous / non-member / wrong role);
- one lane per early stage;
- one lane for everything outside the main object (feeds, admin, webhooks) plus the **API hygiene sweep** (malformed JSON, oversize bodies, wrong method, unknown path, CORS from a foreign origin, security headers, error bodies that leak);
- one **code bug-hunt** lane ([bug-hunter.md](bug-hunter.md));
- at least one **browser** lane, because none of the above sees a pixel.

**Brief from a probe, not from the docs.** Before writing a lane's brief, check its facts against the running system: who can create the lane's objects, who is on each seed's roster, whether the page or route the lane needs is reachable in the seed's current state. Briefs written from reading alone sent lanes to create objects as a role that cannot, and to a page that the seed's state had closed.

Each lane brief names: its part, its objects, its spend budget for paid or model-backed runs, the issues already known for that part (so it does not re-file them), and the model label for its issues. Everything common — tools, rules, findings policy, report format — lives in **one shared brief file** every lane reads first; the per-lane prompt stays short.

Size the fleet by the *target's* capacity as well as the box's: API lanes are nearly free locally, so the limits become the gateway rate limit, the target's worker pool, and how many issues the coordinator can verify.

### The hypothesis loop: code reader → live lane

The code hunt and the live lanes are worth more together than apart.

1. The code lane writes each scenario that needs a mutating test to a shared hypotheses file **as it finds it**: exact calls, timing, expected vs suspected result, and which live lane should run it.
2. The coordinator forwards each one to that lane while it still holds the right state.
3. A hypothesis filed as a latent issue gets its live result as a comment: reproduced (raise the severity) or not in N tries (say so).

Give a code lane a **reading list and a floor**, not only a time box: "read these units in full; do not stop before the list is done". A reader given only a time box can return in minutes with one finding and a long "not covered" list.

### The coordinator watches the logs

Lanes see responses. They do not see what the server and its background workers log while they work. While the lanes run, the coordinator reads the environment's error lines on a cadence and classifies them: pre-existing class, caused by a lane, or new. Faults that live only there — a background job whose configuration differs from the API's, an alarm that fires while its queue is draining, a traceback logged for an ordinary validation refusal — never reach a lane's matrix.

**Verify a lane's high-severity finding yourself before you pass it on** — one call is usually enough — and try it on the next environment down: a defect that also reproduces there is a code defect, not environment data. Use the real clock in every record (`date -u`), never an estimate; lanes and coordinator will disagree on times otherwise.

Also before the first lane starts: confirm no deploy is in flight on the target, and that the API and every background worker run the same build. A roll in the middle of a run turns into a page of false findings.

## What an API run cannot tell you

- Whether the UI offers the move at all, labels it right, or shows the refusal's reason. **Twin every gate finding**: a move the API refuses but the UI offers (or the reverse) is its own bug class ([mischief.md](mischief.md)).
- First paint, async settle, stale client state, layout, keyboard, copy.
- Anything the frontend does between calls (optimistic updates, debounced saves, leave-page saves).

So the diagnostic in [driving.md](driving.md) cuts both ways: findings that are *all* backend mean the front door was skipped; findings that are *all* polish mean the logic behind the door was never attacked. A full run does both, and an API-first run says plainly which pages no lane looked at.

## See also

- [driving.md](driving.md) · [process.md](process.md) · [mischief.md](mischief.md) · [bug-hunter.md](bug-hunter.md) · [findings.md](findings.md)
