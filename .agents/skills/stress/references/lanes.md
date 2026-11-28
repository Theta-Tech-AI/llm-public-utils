---
name: lanes
description: Run many stress testers (lanes) at once on one environment — split the app into lanes, write one shared brief and short lane briefs, start, run and end each lane safely, report in one shape, and coordinate: read the logs, verify findings, feed code-reader hypotheses to live lanes, auto-fix through fixers that pass the three-paragraph gate, land in batches, live-check, and aim the next wave by coverage. Use for API-first campaigns, agent swarms, and any multi-lane stress run.
---

# Lanes: many testers on one environment

A **lane** is one tester (usually a subagent) that owns one part of the app or one property for a time box. API lanes are nearly free on the box, so a coordinator can run many at once ([driving.md](driving.md)); this file is how to keep them productive and safe. How each lane drives: [api.md](api.md) or [browser.md](browser.md). General orchestration (capacity, assignment, review, integration): the `swarm-orchestration` skill, when installed.

## Split the app into lanes

Split by **part of the app**, not by mode: each lane owns one stage or one cross-cutting concern and runs comb *and* mischief on it. A split that worked for a gated authoring app (adapt the names):

- one lane per late stage (review/approval machine · drafting and run control · lock/export/deliverable content);
- one fresh end-to-end flow (the reliability gate, [reliability.md](reliability.md));
- one lane for objects, membership, roles and leases — it also owns the **authorization matrix of the whole API** ([api.md §5.2](api.md#52-the-role-matrix));
- one lane per early stage;
- one lane for everything outside the main object (feeds, admin, webhooks) plus the **API hygiene sweep** ([api.md §5.6](api.md#56-input-and-hygiene));
- one **code bug-hunt** lane ([bug-hunter.md](bug-hunter.md)) and **oracle** lanes ([api.md §6](api.md#6-oracles-one-property-across-everything)), for example a log census — mostly read-only, with any audited reads named in the brief;
- persona lanes, which may run by API ([personas.md](personas.md#personas-by-api));
- at least one **browser** lane, because none of the above sees a pixel (the exceptions: [driving.md → Keep the balance honest](driving.md#keep-the-balance-honest)).

**Which model runs which lane.** The tester's capability is a parameter, and it selects a bug class. A cheap, fast model behaves like a hurried user: it meets the obvious failures soonest and at the lowest cost (5xx, empty or wrong messages, a state that contradicts the last action, dead ends). Run the driving lanes on it first and file those cracks at once. Use a stronger model for lanes that need judgment (ground truth, log clustering, code hunts, the reliability gate, multi-person collaboration) and for the deeper classes once the easy cracks stop coming; fixers and design work need the strongest. A cheap model tends to stop before signed or paid actions and ask: clear those actions explicitly in its brief (which, how many, on which test data), or it reports the step as blocked.

**Size the fleet** by the target's capacity as well as the box's: the limits become the gateway rate limit, the target's worker pool, shared external quotas, and how many findings the coordinator can verify and fix.

## The briefs

**One shared brief** holds everything common, and every lane reads it first: the tools and how to load them, the never-call list, the filing rules ([findings.md](findings.md)) with the labels and the first line of every issue body, the claims file, the cleanup steps and the report shape. **Edit the common block in place.** A brief that grows by appending each wave's new rules under "same rules as the last wave" makes every lane read a chain of headers to learn the rules; a rule that applies to every lane goes into the common block, and a wave header holds only what differs.

**Brief from a probe, not from the docs.** Before writing a lane's brief, check its facts against the running system: who can create the lane's objects, who is on each seed's roster, whether the route the lane needs is reachable in the seed's current state, whether the quota it needs is left. Briefs written from reading alone sent lanes to create objects as a role that cannot, and to a page that the seed's state had closed.

The lane brief stays short:

```text
Lane <NAME> (<model>) — <part of the app or property>; mode <reliability | comb | mischief | oracle | code hunt | persona>
Objects: <ids to reuse, or "create <prefix>-<lane>-<n>">; claim each in <claims file> before the first write
People: <which test user acts in which role>
Budget: paid runs <n>, exports <n>, calls against shared quotas <n>
Known, do not re-file (add evidence instead): <issues>
Ground truth: <where the known-good outputs are>
Deploy gate: <none | wait, with a deadline, until the environment serves build <sha>>
Time box: <about 90 minutes of driving; deploy windows do not count>
Look for: <the classes and readers to compare>
```

The tester's role is to find, prove and file. A lane does not edit or push code; fixers do ([below](#auto-fix-findings-and-gate-every-fix)).

## Start a lane

Before the first lane launches, the coordinator proves the shared tools and the environment once. Then each lane, in this order:

1. **Check the environment and pin the build:** readiness answers OK, no deploy is in flight, and the API and every background worker serve the same build (a roll in the middle of a run turns into a page of false findings). Record that full commit; when the brief has a deploy gate, wait for it first.
2. **Generate the flow map** from that commit, into a new directory, with its receipt ([api.md §1](api.md#1-the-api-document-the-flow-map)); never read a saved copy.
3. **Prove the tools run** in the lane's own checkout before the first real call ([api.md §2](api.md#2-tools-proven-before-the-first-call)).
4. **Check shared budgets.** A third-party service with a daily quota is shared by every lane and by the app's own background work. When the app's own background polling spends such a quota before the lanes start, every lane is blocked from that integration until the reset: the spend is the finding, and every later refusal from that quota is expected, not a finding. Read the remaining quota, the paid-run budget and the claims file before the first write.
5. **Claim the lane's objects**, and post one start entry on the campaign's tracking issue (or in its findings artifact when there is no tracker: [findings.md](findings.md#artifacts-no-github)).
6. **Wait for the reliability gate** before mutating shared seeds ([reliability.md](reliability.md#the-gate)); read code, read state and prepare drivers meanwhile.

## During a lane

- **A deploy window is never a reason to stop.** A 503 "updating" from a rolling deploy stalls a lane; wait for readiness with a deadline, then re-read the commit the API and the workers serve. When it changed, move the checkout to that commit, re-prove the tools, generate a fresh map in a new directory, treat coverage from the old build as old, and say so in the report before you continue. Deploy windows do not count against the time box. Log each window's start and end: a lane can spend more than half its time in update windows, and windows that long are a finding against the deploy, not against the lane.
- **Read the logs** after every surprising answer and every paid run ([api.md → Log cross-check](api.md#log-cross-check)).
- **File as you go**, per [findings.md](findings.md#subagents-must-file-too), and add one line per medium-or-worse finding to the campaign's findings file, `<issue or artifact entry> <severity> <lane> <one-line failure> <class>`, so the coordinator can start a fixer at once.
- **Run the reader table** on every fact the lane's part decides ([api.md §5.1](api.md#51-the-reader-table-one-fact-every-reader-every-role)).
- **Check your own test data** before filing a content finding ([findings.md](findings.md#what-counts-as-a-real-finding)).
- **Work the whole time box.** Progress goes in a clock file in the lane folder, not in messages; send exactly one final report.

## End a lane

Do these even when the lane failed or was cut short:

1. **Release every lease and lock** the lane holds, and free every shared external resource it took (a linked test resource, a reserved name). A lane that ends with a lease still held blocks the next lane on that object.
2. **Archive what the lane created** unless the brief says keep; release the claims; leave reused objects in a stated state (for example: which state, no lease held).
3. **Stop every process the lane started** (browsers, servers, containers) and remove its checkout. Find your own processes by an exact id, never by a name pattern that can match other sessions.
4. **Write the report** and post one end entry on the tracking issue (or the findings artifact).

## The report shape

The final message is at most twelve lines, and its first line is machine-readable:

```text
lane=<NAME> start=<UTC> end=<UTC> calls=<n> medium+=<issue numbers or artifact entries> first-bug-after=<minutes>
```

Then the top defects, what held, paid runs used, and cleanup done. The lane folder keeps `REPORT.md` with: **Findings** (issue, severity, one-line failure, class) · **What held** (the coverage record) · **Not covered**, each with why (a deploy window, a spent quota, a missing read route, no time) · **Needs a decision** · **Cleanup**. The call log stays beside it as the evidence and the coverage input.

A coordinator's wave report on the tracking issue uses the three paragraphs of [findings.md → Talk a bug through](findings.md#talk-a-bug-through-with-the-owner-predict-the-critique) for the wave: the bugs, the fixes in progress, and what the owner will say one level deeper.

## The coordinator

### The coordinator reads the logs

Lanes see responses. They do not see what the server and its background workers log while they work. While the lanes run, the coordinator reads the environment's error lines on a cadence and classifies them: pre-existing class, caused by a lane, or new. Faults that live only there — a background job whose configuration differs from the API's, an alarm that fires while its queue is draining, a traceback logged for an ordinary validation refusal — never reach a lane's matrix.

**Verify a lane's high-severity finding yourself before you pass it on** — one call is usually enough — and try it on the next environment down: a defect that also reproduces there is a code defect, not environment data. Use the real clock in every record (`date -u`), never an estimate.

### The hypothesis loop: code reader to live lane

The code hunt and the live lanes are worth more together than apart.

1. The code lane writes each scenario that needs a mutating test to a shared hypotheses file **as it finds it**: exact calls, timing, expected vs suspected result, and which live lane should run it.
2. The coordinator forwards each one to that lane while it still holds the right state.
3. A hypothesis filed as a latent issue gets its live result as a comment: reproduced (raise the severity) or not in N tries (say so).

Give a code lane a **reading list and a floor**, not only a time box: "read these units in full; do not stop before the list is done". A reader given only a time box can return in minutes with one finding and a long "not covered" list.

### Auto-fix findings, and gate every fix

When the user asked for fixes, the coordinator watches the findings file and starts a fixer for each new medium-or-worse line. Testers keep testing; fixing is a separate pipeline.

- **Group by fact, not by issue.** Findings that are readers of one fact (often from different lanes) go to one fixer, which lists every reader and makes one owner ([findings.md → Fix the issue behind the issue](findings.md#fix-the-issue-behind-the-issue)).
- **Gate every fix** with steps 4 and 7 of that section, exactly as written there; the coordinator's step-4 paragraphs go into the fixer's brief.
- **Land the passing fixes in batches**, by the repository's own merge rules (the `swarm-orchestration` skill's *integrate and deliver* stage covers batching, when installed).
- **Live-check after the deploy.** Each fix leaves a "live check after landing" comment with the exact calls and expected answers; a live-check lane runs each one exactly on the deployed build, closes the issue on PASS with the evidence, and reopens it with the failing call on FAIL.
- Then a sibling lane hunts the same class on other surfaces ("class still open at …" on the closed issue).

### A setup failure is not a result

A lane that never got its scenario running has not tested anything: report it as *not run*, never as *held*. Before a timing window (a deploy, a scheduled job), prove that each start would be accepted: read the allowed actions, and check that the test data is at the right stage. Keep sessions and edit leases alive the way the real client does; a lane that lets its own lease lapse tests the lapse, not the scenario. When a vehicle keeps failing to start, change the vehicle (a prepared object, a longer run, a different stage) instead of retrying the setup.

### Aim the next wave by coverage

A wave that finds no medium-or-worse bug is good news, and also a signal that the lanes are on worn ground. Aim the next wave at what is still on the coverage work list ([api.md §1](api.md#1-the-api-document-the-flow-map)), and at the classes that produced findings, hunted on new surfaces.
