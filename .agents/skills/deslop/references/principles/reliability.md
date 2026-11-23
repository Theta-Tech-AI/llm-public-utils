---
name: deslop-reliability
description: Deslop principles — Reliability: Fail-Fast, No Silent Defaults, Design by Contract, Postel's Law, Errors at the Boundary, Complete Mediation, Resilience & Graceful Degradation, Least Privilege, Boy Scout Rule, Observability.
---

# Reliability

> *Building robust, maintainable systems. These principles govern how code handles errors, maintains itself over time, and operates in production.*

Each principle is a self-contained file — open it when a finding implicates that principle.

## Robustness & Safety

*How does code handle the unexpected? Fail-Fast detects errors early, No Silent Defaults stops absence from masquerading as a value, Design by Contract makes expectations explicit, Postel's Law enables interoperability, Resilience keeps systems running despite failures, Principle of Least Privilege limits damage from breaches, and Complete Mediation puts a rule every member must obey where every member passes.*

| Principle | What it says |
|-------------|----------------|
| [Fail-Fast & Defensive Programming](reliability/fail-fast.md) | Detect and report errors at the earliest possible moment |
| [No Silent Defaults](reliability/no-silent-defaults.md) | Model absence explicitly; never synthesize a plausible value for it |
| [Design by Contract](reliability/design-by-contract.md) | Explicit preconditions, postconditions, invariants |
| [Postel's Law (Robustness Principle)](reliability/postels-law.md) | Strict output, tolerant input; paranoid at security boundaries |
| [Errors at the Boundary](reliability/errors-at-the-boundary.md) | **Detect at the edge, translate at the seam, decide where the context is.** Every `catch` must name a decision; a handler that only logs and continues, or re-raises unchanged, is a misplacement. Tells: `except Exception: log(e)` in a service; `if "duplicate key" in str(exc)` at a controller — string-matching a driver's message instead of an error type at the seam; a validator called from twelve leaves because the value was never made safe where it entered; a lower layer's exception type in a public signature; `raise X()` without `from`, losing the cause. Count the seams between throw and catch: more than one means nobody translated |
| [Complete Mediation](reliability/complete-mediation.md) | **A rule every member of a population must obey is enforced where every member passes, on by default, and confirmed under the write lock.** A call each member must remember is a check the member that forgot does not have, and nothing fails. Tells (structural): the enforcing call appears N times and the population (the route table, the handler registry, the writers of a table) has M > N members; two or more helpers enforce one rule with different meanings; a fix that adds a helper for one more group of members; the edge declares the role and the lease, audit or tenant filter is added by hand further in; an exemption only a comment states; a refusal with no audit record because the audit write sits behind the check. Build the **population census** (`readings/auditing.md`) and read the empty cells |
| [Resilience & Graceful Degradation](reliability/resilience.md) | Retry, fall back, circuit-break; design for partial failure |
| [Principle of Least Privilege](reliability/least-privilege.md) | Minimum permissions per component |

## Maintainability & Operations

*Code is a living artifact. The Boy Scout Rule keeps code improving incrementally with every change, while Observability & Transparency ensure you can understand what your systems are doing in production.*

| Principle | What it says |
|-------------|----------------|
| [Boy Scout Rule](reliability/boy-scout-rule.md) | Leave code better than you found it, scoped to what you touch |
| [Observability & Transparency](reliability/observability.md) | Structured telemetry as your production debugger |
