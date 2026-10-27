---
name: personas
description: "Run the app as a panel of distinct first-time users — independent persona agents each landing-page-to-first-success, confusion captured live — then merge findings ranked by how many personas hit them and rerun the identical panel to prove the fixes. Use for launch QA, onboarding pressure, 'test it as different users', or when one driver's temperament is the blind spot."
keywords: [personas, subagents, launch-qa, first-time-user, onboarding, frequency-ranked, rerun, mobile, accessibility]
---

# Personas: The First-Time-User Panel

One driver has one temperament — yours. You know the app, you click in the right order, you read the labels, and you forgive the rough edges because you already know what they were meant to say. That is a **blind spot with a shape**: every bug that only fires for an impatient thumb, a literal reader, or someone on a throttled phone is invisible to a sweep run by a single well-informed agent. Comb narrows the happy path; mischief refuses it; the panel tests **whose** happy path the app was built for.

Same rules as every mode: [driving.md](driving.md) for the hands, [findings.md](findings.md) for what happens to a bug.

## When to run the panel

- A **launch** or onboarding change is about to meet strangers.
- The user says "test it like a real user", "as if I'm new here", "5 different users", "what confuses people".
- After comb and mischief have gone quiet — the panel is how you find the class of bug that *isn't* a defect in any one flow, but a mismatch between the flow and the people who will drive it.

It is **not** a substitute for the reliability gate: personas run on a system whose happy path already completes, and each persona's own run ends the moment it can't. A panel on a broken build is five confused agents reporting the same 500.

## The default panel

Five personas, deliberately unlike each other. Each one is a **behavioral contract**, not a costume: it changes what the agent clicks, what it reads, when it gives up, and what it does not bother to try. It does **not** change the language the agent reports in, its competence at driving the browser, or its honesty about what it saw.

| Persona | Behavior contract | What it is built to catch |
|---|---|---|
| **The impatient one** | Skims. Clicks the first plausible button. Never reads helper text. Quits at the first error or unexplained wait. | Unclear primary CTA, error copy that doesn't say what to do next, first-step friction, silent spinners |
| **The skeptic** | Reads pricing, terms and privacy *before* signing up. Looks for what happens to their data, what the trial costs, how to leave. | Missing/hidden terms, price ambiguity, dark-pattern or trust-breaking gaps, "sign up to find out" walls |
| **The mobile user** | 375px viewport, mobile UA, throttled network, thumb-sized targets, real scroll. | Overflow, occlusion, tap targets, layout that needs hover, loads that time out on a slow link |
| **The literal reader** | Follows only what the UI says, word for word. No inference from context or prior product knowledge; ambiguous labels are taken at face value. | Copy that assumes insider knowledge, jargon, labels that misdirect, instructions that contradict the affordance |
| **The breaker** | Pastes junk into forms, hits Back mid-flow, double-clicks everything, refreshes on a submit. | Validation gaps, state loss, duplicate actions, unsaved-change loss — *breadth-first jitter*, not deep hostility |

**Add or swap one persona when the product has a real one.** A ranking-parcel tool has a skeptic about valuation; a clinical product has a clinician in a hurry; a marketplace has a seller, not only a buyer. Ground the addition in the product's actual audience, and say in the report which personas ran — a panel is evidence only if the reader knows who was in the room.

**The breaker's boundary:** mischief already owns deep, escalating abuse. This persona contributes **jitter** — the shallow hostile habits of a real person — and its findings are added to the panel's ranked list like any other. Do not let it become a mischief run that happens to have four colleagues.

## Independence — the thing that makes the panel worth its cost

1. **One subagent per persona.** Five agents in one context contaminate each other: the second persona learns the app from the first, and the report collapses into one agent's opinion five times. Spawn them in parallel, each with its own browser session (`--session <persona>`).
2. **Fresh state each.** New account, empty storage, cold cache, no saved session — unless the persona's contract explicitly involves a returning user.
3. **Identical scope and stop rule.** Every persona gets the *same* start URL, the same definition of "first success" (state it in the dispatch: "you have succeeded when a document is generated and visible"), the same time budget, and the same instruction: stop when first success is reached, or when you would quit in real life — **record where you quit**.
4. **No knowledge injection.** The dispatch tells the persona what a first-time user sees, never how the app works, what the intended path is, or where the known rough patches are. A persona briefed on the fixes is a test of the brief.
5. **Same target, same SHA.** Every persona runs the same deploy. Write the commit/SHA in the report — a panel split across two builds is not one experiment.
6. **Each persona files its own findings** — explicitly required in the dispatch, per [findings.md](findings.md). A persona that returns bugs only in its final message loses them with the session.

## Per-persona run protocol

Cold open → pursue first success *in character* → at every moment of confusion, being stuck, or being annoyed, **capture** → finish or quit.

Capture, at the moment it happens (not from memory afterwards):

```bash
agent-browser screenshot ~/qa/panel/<persona>/<n>-confused.png
agent-browser snapshot -i -c      # what the user could actually see/act on
agent-browser network requests --status 4xx --status 5xx   # the UI lies by omission
agent-browser console
```

Log one line per event: `timestamp · persona · step · what I expected · what happened · severity guess`. The **quitting point is the most valuable data point in the run** — the step where a real person leaves is the step that costs the most money.

Screenshot the *confusion moments*, not every step: a persona that photographs 200 pages has produced an expensive film nobody will watch, and an image-blind reviewer cannot read it. The text record (snapshot + console + network + the event log) is the evidence; screenshots illustrate the ones that matter.

### The mobile persona, concretely

```bash
agent-browser set viewport 375 667
agent-browser --user-agent "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" open <url>
agent-browser set offline on   # …and back off mid-flow: the resume matters more than the drop
```

The CLI has no bandwidth throttle, so approximate a slow link with a latency shim registered before the first navigation — and **say so in the report**, because it delays the app's own calls rather than shaping the pipe:

```bash
cat > ~/qa/panel/slow3g.js <<'JS'
const delay = 400;
const wrap = (fn) => function (...a) { return new Promise(r => setTimeout(() => r(fn.apply(this, a)), delay)); };
if (window.fetch) window.fetch = wrap(window.fetch);
const open = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.send = function (...a) { setTimeout(() => open.apply(this, a), delay); };
JS
agent-browser --session mobile --init-script ~/qa/panel/slow3g.js open <url>
```

## Merge and rank

After the panel returns, **merge into one list** — the same defect hit by three personas is one entry with a count of three, not three entries. Then rank:

| Rank order | Why |
|---|---|
| **How many distinct personas hit it** | Frequency across independent temperaments is a real severity signal — a defect 4/5 strangers meet is not a polish item, whatever the code thinks |
| **Then: blocked first success** | Anything that stops a persona reaching the goal outranks friction that merely annoys |
| **Then: abandonment** | A persona who quit at that point is the highest-value evidence you have |
| **Then: severity within the tier** | Data loss > wrong data > blocked > confusing copy > cosmetic |

A **1/5 finding is still a bug** if it blocks first success or loses data — frequency ranks attention, it does not acquit. And a persona that sailed through cleanly is a result too: name it, so the report shows which temperaments the product already serves.

The ranked list is a *panel* view: it does not replace the individual issues filed by each persona. Comment the count and the persona list onto each filed issue so the triage decision carries the breadth signal.

## Fix, then rerun the identical panel — the proof

Fixing is not proof. The panel is rerun **as an experiment**, and the experiment is only valid if nothing but the product changed:

1. **Bound the fix pass.** Fix the panel's top findings as one scoped pass — small, additive, tested knots as [findings.md](findings.md) allows; load-bearing ones get filed and cited, not silently rewritten mid-run. Record the fixed SHA.
2. **Freeze the scripts.** The persona briefs, start URL, definition of first success and event format are **byte-identical** to run one. Change any of them and you have tested a different panel.
3. **Rerun blind and fresh.** New subagents, new accounts, new sessions, no fix list, against the fixed deploy. A persona told "we fixed the CTA" will find it.
4. **Report persona-by-persona and finding-by-finding:** who completes now, who still abandons and exactly where, which entries are closed, which regressed, which are new. State which findings the fix pass did **not** address, so "5/5 complete" is never read as "everything fixed".
5. **Verify the rerun target is the fixed build** — the SHA in the rerun report must match the fixed SHA. A rerun against a stale deploy is a re-run of run one and proves exactly nothing.

A defect that survives its own fix is the most valuable output the panel can produce: file it with both runs' evidence attached, and say plainly that the first fix did not hold.

## Anti-patterns

- **One agent role-playing five personas in sequence.** Cheap, and worthless: contamination plus one temperament wearing five hats. Independence is the method.
- **Personas that only differ in adjectives.** "Frustrated user" vs "confused user" is not a behavioral contract. The contract must dictate *actions* — what is read, what is clicked first, when it quits.
- **Briefing personas on the app.** Handing them the intended happy path turns launch QA into a script-following exercise that confirms the design instead of testing it.
- **Fixing everything in one heroic pass** without filing. Findings die with the session; file per [findings.md](findings.md) first, fix what is safe, cite the rest.
- **Declaring victory from the rerun's tone.** Count completions and closures, not enthusiasm — "4/5 reached first success, 6 of 9 findings closed, 2 filed, 1 regressed" is the sentence; nothing softer.
- **Running the panel instead of comb and mischief** on a system nobody has driven yet. The panel is a breadth instrument on a working product, not a first contact.

## See also

- [process.md](process.md) — where the panel sits in the standard run (an optional phase 2-alternative / post-comb instrument)
- [comb.md](comb.md) — gentle happy-path grooming by one deliberate driver
- [mischief.md](mischief.md) — hostile, deep, escalating abuse
- [driving.md](driving.md) — browser vs API, resize, occlusion, truth-checks
- [findings.md](findings.md) — filing rules, including the subagent rule this mode depends on
