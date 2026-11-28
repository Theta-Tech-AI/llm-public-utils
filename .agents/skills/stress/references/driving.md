---
name: driving
description: The two drive modes of a stress run — API and agent browser — as dueling lenses. What each is, why it works, why it matters, what only it can find, what it costs, and how to run them against each other so that each catches what the other cannot. Read before choosing how to put hands on the system.
---

# Driving: two modes, dueling

Stress testing needs hands on the system, and there are two kinds. **API mode** talks to the backend the way every client does. **Browser mode** uses the real UI the way a person does. They are not a fast mode and a thorough mode: they are two lenses that see different bugs, and each is strongest when it checks the other. How to drive each: [api.md](api.md) · [browser.md](browser.md).

## API mode: the contract every client inherits

**What it is.** A script sends the same HTTP calls the frontend sends, as every role, in any order, with no browser.

**Why it works.** The API is one layer deeper than any page. Every frontend, mobile app, integration, agent and future client goes through it, and none of them can be safer than it: a page can hide a move, but anyone with a token can still make it. So **a bug in the API is a bug in every client at once**, one API finding covers every surface, and a fix there fixes them all. The UI also hides most of the state space — it offers only the moves it thinks are legal, as the signed-in role, in the order its pages lead. The API lets you make every other move: out of order, twice at once, as another role, with a stale version, against another tenant's object; and it gives you the server's own answer and its own refusal, unfiltered by a page.

**Why it matters.** Data loss, authorization holes, races, audit gaps, silent corruption, and status messages that contradict the rules never show on a screen until they bite a person — and then they bite everyone who uses that route.

**What only it finds, or finds far faster.** One fact that different readers state differently (the reader table, [api.md §5.1](api.md#51-the-reader-table-one-fact-every-reader-every-role)); a move the UI hides but the server accepts; role × state matrices; races with exactly-one-effect checks; refusal typing and refused-action audit records; out-of-order and change-of-mind sequences; late stages of a gated flow that browser runs reach last and least; the content of exports and generated output against ground truth; the background work behind a 202.

**Cost and speed.** Each probe is one HTTP round trip: no browser start, no rendering, no waiting for a selector, no screenshot to read. In one overnight API-only campaign against a gated, multi-role web app, the lanes of one wave that wrote full reports made **169 to 344 calls each in 27 to 37 minutes**; that wave ran eight lanes at once from one machine; each script acted as every person of a four-person team (owner, editor, two reviewers) in the same minute; a ten-reader, three-role reader table took a few minutes and reproduced 3 of 3. Every repro is a call list anyone can run again, with no render flake; for timing-dependent bugs such as races, record the timing and how often it reproduces (N of M). What limits API mode is the target, not the tester: the gateway's rate limit per IP, the worker pool, paid runs, and deploy windows.

**What it cannot see.** Whether the UI offers the move at all, labels it right, or shows the refusal's reason; first paint, the async settle, stale client state, layout, keyboard, focus and copy as rendered; anything the frontend does between calls (optimistic updates, debounced saves, leave-page saves).

## Browser mode: what the person actually experiences

**What it is.** An agent drives the real UI in a real browser: it clicks, types, waits, reads and resizes like a user.

**Why it works.** The person never sees the API. Their whole experience is what renders, when it renders, what it says, and whether the controls behave. And the frontend is a second decider: it filters, caches, re-derives and times what the server said. Each of those steps can be wrong while the API is right — a page that re-decides a fact the server already decided is its own bug class.

**Why it matters.** Bugs that real people report first skew heavily to this class, because backend-first sweeps never see them ([findings.md → Learn from bugs users found first](findings.md#learn-from-bugs-users-found-first)). A clean API under a confusing page still loses the user.

**What only it finds.**

- gate or nav state that disagrees with the backend's prerequisite state (a reachable stage with an unmet predecessor);
- first-visit and transient render races (stale "not ready" until a manual refresh; a control that flashes, then hides);
- a raw internal value that flashes before its lookup resolves;
- loading-state and progress-indicator polish; blank read as "no data";
- error and status copy that a person cannot act on;
- hide-vs-disable, dead-end panels, occluded controls, layout at other widths, keyboard traps;
- optimistic UI that claims a save the server never made.

**Cost and speed.** A browser session costs gigabytes of memory and seconds to minutes per step; one session acts as one role; refs go stale on every re-render; timing makes some runs flaky. Spend it where it pays: on the paths people walk.

## Choose the lead mode by the question

| The question | Lead with | Also run |
|---|---|---|
| "Does this webapp feel right / will strangers get through it?" (UX, launch, onboarding) | browser (and the [persona panel](personas.md)) | API to seed state and confirm backend truth |
| Contracts, state machines, authorization, concurrency, idempotency, audit, data integrity | API | one browser lane on the user paths that touch them |
| The late stages of a gated flow; many repetitions; many roles at once | API | browser twins for each gate finding |
| An agent swarm, or a box that cannot afford many browsers | API ([lanes.md](lanes.md)) | at least one browser lane ([exceptions](#keep-the-balance-honest)) |
| The surface is API-native (CLI, mobile backend, partner integration) | API | — |
| "Stress test this" on a webapp | both, per [process.md](process.md) | — |

## How to duel them

When both modes run — the default for a webapp:

1. **API first, to map and hammer.** Generate the flow map, then run the reader table, the role matrix, out-of-order moves and races cheaply, standing on late-stage objects ([api.md](api.md)). This finds the contract, state, authorization and concurrency bugs — every one of them a bug in every client.
2. **Browser on the paths people walk**, aimed by what the API pass found load-bearing: the frontend playbook in [browser.md](browser.md).
3. **Cross the results.** A disagreement between what the API says and what the page shows is itself a finding: the frontend has re-decided the producer's fact (if the `deslop` skill is installed, its pattern *consumer re-decides producer* names it). **Twin every gate finding**: a move the API refuses but the UI offers, or the UI blocks but the API allows, is a real bug either way.
4. **Hybrid patterns** with high leverage:
   - **API setup → browser verify.** Seed and reset state by API; comb or attack only the UI that matters.
   - **Browser discover → API amplify.** Turn a suspicious UI sequence into a script with variants, roles and concurrency.
   - **API assert while the browser drives.** During a UI pass, read the same resources by API and compare with what renders.
   - **HAR bridge.** Capture a HAR in the browser and turn its hot paths into API scripts.

## Keep the balance honest

**For a webapp, the front door is not optional.** Every backend route exists to serve what renders; a pass that only probes the API or reads code over-reports backend defects and misses the UX, state, timing and copy bugs that actually reach people. **And API-first is not skipping the front door.** For contract, state, authorization and concurrency hunts and for agent swarms it is the right lead, because it finds the class every client inherits, fastest — as long as some browser lane walks the user paths (unless the request is API-only, the user declined a browser, or the target has no UI; say so in the report).

The diagnostic cuts both ways. Findings that are *all* backend mean the front door was skipped; findings that are *all* polish mean the logic behind the door was never attacked. A full run does both, and an API-first run says plainly which pages no lane looked at.

## A third surface: logs and infrastructure

Server and worker logs, deploy runs and cloud state show what neither a response nor a page shows: what the background work did, and whether a deploy was rolling. They are the second layer for every finding ([api.md → Log cross-check](api.md#log-cross-check)) and the first check before a 502, a blank page or a stale chunk is filed ([findings.md](findings.md#what-counts-as-a-real-finding)).
