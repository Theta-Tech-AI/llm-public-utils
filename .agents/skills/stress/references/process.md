---
name: process
description: The standard stress run — set up (environments, access, drive modes), then 1-3 reliability passes, 1-3 comb passes, and 1-3 mischief passes, with the code-first bug hunt last or in parallel and the persona panel before a launch, filing findings throughout. Use as the default shape of a full stress engagement, and for when to deviate from it.
---

# Process: the standard stress run

A full stress run has a shape. Not a straitjacket — user intent and whatever you find always win — but a default that keeps you from red-teaming a system whose happy path is broken.

| Phase | File | Passes | Question it answers |
|-------|------|--------|---------------------|
| 0 | Set up (below) | once | Where may I stress, with which access, by which mode? |
| 1 | [Reliability](reliability.md) (the gate) | 1-3 | Does the happy path *consistently* complete? |
| 2 | [Comb](comb.md) | 1-3 | Where are the knots on and around the happy path? |
| 2b | [Persona panel](personas.md) (optional; the default before a launch) | 1, then a rerun | Will strangers get through it, and where do they quit? |
| 3 | [Mischief](mischief.md) | 1-3 | What breaks under hostile, out-of-order abuse? |
| 4 | [Bug hunt](bug-hunter.md) | once per area | What do layers, workflows, and data models hide? |

Each phase hands context to the next: reliability proves the path works, comb maps where it is rough, mischief attacks whatever turns out to be load-bearing, and the bug hunt finds the code address of every knot and crack. A failed reliability gate **ends the run early**: there is no point combing or attacking a system that cannot reliably do its one job.

## Phase 0 — Set up

**Know the environments.** A stress run needs at least one environment where the happy path can run. Web apps usually have layers, some missing, some under CI/CD (scout the pipeline files to learn how each deploys; ask if unclear):

1. **localhost** — rapid code iterations and local development.
2. **Cloud development** — a no-cost-to-break cloud deployment, per developer or shared.
3. **Cloud staging** — as close to production as possible, for quality assurance before production; real-user pretending happens here.
4. **Production** — never touch it unless explicitly instructed, and confirm any production change with the user before acting. It is a final "works just like staging" check, not a feedback loop: reproduce a production-only bug on staging first.

**Get access.** Auth may live in env vars, docs, a local-dev skill, token scripts, or a bypass. Use throwaway accounts and data, one per role you need.

**Choose the drive modes** from [driving.md](driving.md): browser for what renders, API for contracts, state, authorization and concurrency, and both for most webapps. Ask consent before installing a browser ([browser.md](browser.md#consent-first)).

**Read [findings.md](findings.md) before the first pass**: findings are filed as they are confirmed. Confirm the reporting policy with the user only if they contradicted it.

## Phase 1 — Reliability gate (1-3 passes)

Run the primary happy path end to end, up to three times; pass and fail rules are in [reliability.md](reliability.md). Fail = stop, file, and hold the run here.

## Phase 2 — Comb (1-3 passes)

Groom the path per [comb.md](comb.md): repeat it with slight deviations, start wide, go finer each pass.

## Phase 2b — Persona panel

Five independent first-time users replace the driver and record where they get confused or quit ([personas.md](personas.md)). Run it **instead of** a comb pass when the question is "will strangers get through this?", and **after** comb for a breadth signal before release. It assumes the reliability gate passed and does not replace mischief.

## Phase 3 — Mischief (1-3 passes)

Now that you know the happy path cold, refuse it per [mischief.md](mischief.md). Aim the waves at whatever Phase 2 revealed as load-bearing.

## Phase 4 — Bug hunt (last, or in parallel)

Code-first, per [bug-hunter.md](bug-hunter.md). It never touches the running app, so it may run **in parallel** (a subagent reading code while you drive phases 1-3) or as the final sweep. Feed it what the earlier phases smelled: every knot and crack has a code address.

## Throughout

- **File findings as you go** per [findings.md](findings.md); never batch them to the end.
- **Cross-check every finding** on a second layer before you believe it ([findings.md](findings.md#what-counts-as-a-real-finding)).

## When to deviate

- The user asked for one mode only → run that mode. This process is the default for an open-ended "stress test this."
- A launch or onboarding change is about to meet strangers → insert Phase 2b, and rerun the same panel after the fixes as its own proof step.
- The findings are all polish and the panel has not run → the temperaments you did not try are the unexplored surface; run the panel before concluding the app is clean.
- The late stages of a gated app are under-tested, the box cannot afford browsers, or the user asked for an API-only run → run the requested phases **API-first** ([api.md](api.md)): the generated flow map first, then the reliability gate as one fresh end-to-end flow (code reading, state reads and driver preparation may run meanwhile), then whichever of comb and mischief the request includes, standing on existing late-stage objects. With many testers ([lanes.md](lanes.md)): one lane per part of the app, one code hunt feeding hypotheses to the live lanes, and at least one browser lane (exceptions: [driving.md → Keep the balance honest](driving.md#keep-the-balance-honest)).
- Time-boxed → one real pass per phase beats three shallow ones or skipping a phase.
- Phase 1 keeps failing → the run legitimately ends early; a broken happy path *is* the headline finding.
