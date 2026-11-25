# Oracle lanes: let a property judge, not a script

A driving lane walks one path and finds what breaks on it. An **oracle lane** checks one property across everything the system does, and finds a *class*. Most oracles are read-only and cheap, so run them beside the driving lanes, not after them. Each finding is a class with one owner, filed with the one-level-deeper paragraph from [findings.md](findings.md).

## The oracles

| Oracle | The property | How to run it | What it finds |
|---|---|---|---|
| **Consistency** | Every reader of a status agrees with what the action does | For each action a state endpoint offers or refuses, read what it says (allowed, who acts next, the blocker text), then call the action as each role and compare | A status line that names the editor while the route needs a reviewer; `allowed: true` and a refusal; a blocker that names a move that does not exist. The decision behind it: a status and its message were never made one fact |
| **Cost** | No paid work repeats a finished result for the same inputs unless a person explicitly asked for it | Do the everyday actions (save unchanged, unlock and re-lock, re-submit, send and return, re-pick) and record every paid run each one starts; a retry after a failure, or an explicit request to generate again, is not a finding | Re-runs decided by an event or a time instead of the inputs; one click that starts two runs |
| **Liveness** | Every running or waiting state moves within a bound, or names who it waits for | Every few minutes for an hour or two, list queued, running and cancelling work and every waiting state from one system-wide run list (sampling each project's newest run misses work that starts and ends between samples); investigate anything that has not moved | Silent stalls, cancels that never finish, work queued behind nothing |
| **Log census** | Every distinct error and warning class has an owner | Pull a day or two of error and warning lines, cluster them by site and cause, and match each class to an open issue | Failures nobody filed because each one looked like noise; counts that show which class costs most |
| **Run census** | Every failed or cancelled background run has a named cause | List the failed and cancelled runs of a period, group by kind and cause | Unclassified failures; a cancel reason that is not what happened; one cause behind many kinds |
| **Ground truth** | A generator's output covers what a known-good output covers, faithfully | Where real finished examples exist, compare the generated output with them by section: length, the key facts present, missing or wrong, unsupported claims | Systematic gaps by class (a table never filled, a fact always missed), not a per-sentence list |
| **Record** | What is delivered is exactly what was approved | Export after an approval; compare each delivered document's content and version identity with the approved version (the version the approval bound, not the newest one; and after only the transformations the product declares, such as rendered citations and added headings), and check every file against its own manifest entry; export twice and diff the content, allowing only the parts the product declares variable (timestamps, provenance, signature material), and require byte equality only where the product promises it | Unapproved text in a delivery; a manifest that does not match its files; a second export whose content differs |

## Rules

- **Write the property down first**, in one sentence, before the lane looks at anything. A lane that starts browsing for problems becomes a comb pass.
- **A finding is a class.** Report the property, every instance found, and the one place that should own the fact. Twelve instances of one class are one issue with twelve rows.
- **The oracle needs a ground.** Consistency needs the route's real answer, cost needs the run list, ground truth needs a known-good output. If the ground is missing, say so and stop; do not guess it.
- **Check the ground before you report.** A surprising result is often a wrong ground: the newest version instead of the approved one, or a tool that silently defaults to another environment (print the target before every conclusion; "everything vanished" usually means you asked the wrong place).
- **A read can write.** On audited systems, downloads and some reads append audit records. Find out before you call a lane read-only, and ask whoever owns the environment before you add records to a shared trail.

## Who runs which lane

The tester's capability is a parameter, and it selects a bug class. A cheap, fast model behaves like a hurried user: it meets the obvious failures soonest and at the lowest cost (5xx, empty or wrong messages, a state that contradicts the last action, dead ends). Run the driving lanes on it first and file those cracks at once. Use a stronger model for the oracles that need judgment (ground truth, log clustering) and for the deeper classes once the easy cracks stop coming.

A cheap model tends to stop before signed or paid actions and ask. Clear those actions explicitly in its brief (which, how many, on which test data), or it reports the step as blocked.

## A setup failure is not a result

A lane that never got its scenario running has not tested anything: report it as *not run*, never as *held*. Before a timing window (a deploy, a scheduled job), prove that each start would be accepted: read the allowed actions, and check that the test data is at the right stage. Keep sessions and edit leases alive the way the real client does; a lane that lets its own lease lapse tests the lapse, not the scenario. When a vehicle keeps failing to start, change the vehicle (a longer run, a different stage) instead of retrying the setup.

## See also

- [api-flows.md](api-flows.md): the flow map and the move × state × actor matrix the consistency oracle walks.
- [personas.md](personas.md): the first-time-user panel; oracles find classes that no single person meets.
- [findings.md](findings.md): filing a class, and talking it through with its owner.
