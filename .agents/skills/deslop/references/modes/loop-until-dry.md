---
name: deslop-loop-until-dry
description: Iterate deslop passes until a full scan yields nothing actionable — fix, re-verify, re-scan, then a second-model final pass, with guardrails.
---

# Loop until dry

A single pass is a sample, not a verdict. When the user asks for thorough
desloping (or says "keep going"), iterate: fix the violations you found,
re-verify (tests + typecheck + build), commit the loop, then RE-SCAN the
same scope with fresh eyes — each extraction or sweep tends to expose the
next layer (a dedup reveals drift between the copies; a token sweep reveals
the off-scale literals the first regex missed). Stop only when a full scan
of the scope yields nothing actionable, then have a second model
(e.g. `codex` with this same skill) do an independent final pass: a
different prior reliably finds violations the first reviewer normalized.
Two guardrails while looping: pin every behavior-adjacent fix with a test
that was red before it (a refactor with no failing-test proof is a hope,
not a fix), and respect the [meta-principle](when-to-relax.md#the-meta-principle) — when a "violation" survives
scrutiny because fixing it makes the code worse, record WHY and move on
rather than churning.
