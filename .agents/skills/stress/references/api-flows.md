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
| **Token source** — per-user file, refreshed under a per-user lock, expiry checked before each call. | Lanes run longer than a token lives; two lanes minting one user at once break each other. |
| **Signed-step helper** — whatever the app needs for a re-authenticated or confirmed step. | The most valuable late-stage tests need it; each lane re-deriving it is hours lost. |
| **Logs helper** — one command that reads the server and worker logs of the target environment. | The second layer for every finding (see [findings.md](findings.md)). |
| **Code tree at the deployed commit**, read-only. | Route list, bodies, and the code pointer every issue needs. |

### One pacing gate for the whole box

A gateway or WAF rate limit is **per client IP**, and every lane on one machine shares that IP. Ten lanes that each pace themselves politely still add up to a burst. Put the gate in the shared client: one lock file, a minimum interval between any two calls box-wide, and an explicit opt-out flag for a deliberate race of a few calls. Find the real limit in the infrastructure code before choosing the interval.

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

Also before the first lane starts: confirm no deploy is in flight on the target, and that the API and every background worker run the same build. A roll in the middle of a run turns into a page of false findings.

## What an API run cannot tell you

- Whether the UI offers the move at all, labels it right, or shows the refusal's reason. **Twin every gate finding**: a move the API refuses but the UI offers (or the reverse) is its own bug class ([mischief.md](mischief.md)).
- First paint, async settle, stale client state, layout, keyboard, copy.
- Anything the frontend does between calls (optimistic updates, debounced saves, leave-page saves).

So the diagnostic in [driving.md](driving.md) cuts both ways: findings that are *all* backend mean the front door was skipped; findings that are *all* polish mean the logic behind the door was never attacked. A full run does both, and an API-first run says plainly which pages no lane looked at.

## See also

- [driving.md](driving.md) · [process.md](process.md) · [mischief.md](mischief.md) · [bug-hunter.md](bug-hunter.md) · [findings.md](findings.md)
