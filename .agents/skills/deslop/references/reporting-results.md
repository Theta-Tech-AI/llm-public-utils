---
name: deslop-reporting-results
description: How to report a deslop pass to a person — lead with the answer, bucket the work, keep it short, and never bury it in method.
---

# Reporting results

**Read this immediately before you say anything to the person who asked.** Everything before it produced a
consolidated, bucketed, concern-level list; this stage decides the shape of the sentence.

The failure it prevents: the worker's instinct to narrate the method. Cells enumerated, groups assigned, 55 raw
findings, 34 disputed loci, four waves, two scripts, a control table — all true, all noise to someone deciding what
to fix on Monday. **Lead with the answer, then justify it in one line each.**

## 1. The shape

Four parts, in this order, and no fifth:

1. **The headline** — one or two sentences. What the pass covered, and the single most important thing it found.
   Numbers with denominators: "42 findings across 9 modules; three are load-bearing."
2. **Now** — the short list that should be fixed first. Three to seven items, each one line: locus, what is wrong,
   why it matters, and the repair in two words. This is the part people act on; make it scannable.
3. **Next** — the contained work, as a compact list or a small table. One line each. No prose.
4. **Left out** — what was skipped, relaxed, or never surveyed, plus the condition that would change the bucket of
   anything contentious ("if this becomes public API, the duplication becomes a defect"). Include the **rotation
   state** in one line: which principle groups this round exercised, and **which remain unread on this target**.
   That line is what tells the reader a second round is worth commissioning — and what proves this one was not a
   repeat of the last.

Then stop. If they want the derivation, they will ask, and the report files are already written for that.

## 2. Rules of the register

- **Concise beats complete.** A pass that produces forty findings produces a report of at most a dozen lines
  before the reader stops reading. Group; do not enumerate.
- **One paragraph of prose at most**, and only for the headline or a genuinely subtle judgement. Lists and small
  tables for everything else.
- **Numbers carry denominators**: "12 of 14 cells fired", "34 of 55 findings are in one module". A bare count
  invites the wrong question.
- **Severity in words a human uses**: "silently returns the wrong total", not "high". The label is a shortcut, the
  consequence is the information.
- **Quote a line of code only when it is the point.** A finding whose evidence cannot be understood in one
  sentence is not ready to report.
- **Name the owner.** "No component owns provider-credential parsing; three adapters do it themselves" is a
  report. "DRY violation in azure_openai.py:71" is a chore.
- **No method unless asked.** The plan, the scripts, the merge tables, the control runs — one line at the end at
  most ("artifacts: `plan.md`, `merged.md`"), never in the middle.
- **Never end with a permission question** when the next step is in scope. File the issue, order the milestone,
  then report what you did.

## 3. Template

```
<One or two sentences: what was reviewed, and the most important finding.>

**Fix first**
- `<file>:<line>` — <what is wrong> → <repair>. <Consequence in one clause.>
- ...

**Next** (<n> items, milestone <name>)
- `<file>:<line>` — <what is wrong> → <repair>
- ...

**Left out** — <skipped cells>, <relaxed findings, and why>, <areas not surveyed>.

<Optional single line: artifacts / where the full list lives.>
```

## 4. Anti-patterns

| Instead of | Write |
|---|---|
| a table of 40 rows | 5 "fix first" items, the rest grouped under their concern with a count |
| "the swarm enumerated 45 candidate cells and selected 16" | "16 readings; the boundary group found what the general pass never opened" |
| "high severity" | "every request takes the silently-wrong branch" |
| "shall I file these?" | filed, with the numbers, or explicitly out of scope and why |
| a status of the machinery ("4 of 8 agents returned") | the result ("42 findings, 3 load-bearing") |
| "there is a lot here, let me know where to start" | your recommendation, in order |

## 5. One last check

Before sending, read it as the recipient: can they decide what to do in the first ten seconds? If the first
sentence is about the process rather than the code, rewrite it.
