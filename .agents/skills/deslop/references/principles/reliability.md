---
name: deslop-reliability
description: Deslop principles — Reliability: Fail-Fast, No Silent Defaults, Design by Contract, Postel's Law, Errors at the Boundary, Complete Mediation, Resilience & Graceful Degradation, Liveness, Least Privilege, Boy Scout Rule, Observability.
---

# Reliability

**Why this is slop:** the expensive slop fails silently: the work completes on a false premise and the incident surfaces later, far from where the truth was dropped.

> *Building robust, maintainable systems. These principles govern how code handles errors, maintains itself over time, and operates in production.*

Each principle is a self-contained file — open it when a finding implicates that principle.

## Robustness & Safety

*How does code handle the unexpected? Fail-Fast detects errors early, No Silent Defaults stops absence from masquerading as a value, Design by Contract makes expectations explicit, Postel's Law enables interoperability, Resilience keeps systems running despite failures, Principle of Least Privilege limits damage from breaches, and Complete Mediation puts the authority check inside the one door every change passes.*

| Principle | What it says |
|-------------|----------------|
| [Fail-Fast & Defensive Programming](reliability/fail-fast.md) | Detect and report errors at the earliest possible moment |
| [No Silent Defaults](reliability/no-silent-defaults.md) | Model absence explicitly; never synthesize a plausible value for it |
| [Design by Contract](reliability/design-by-contract.md) | Explicit preconditions, postconditions, invariants |
| [Postel's Law (Robustness Principle)](reliability/postels-law.md) | Strict output, tolerant input; paranoid at security boundaries |
| [Errors at the Boundary](reliability/errors-at-the-boundary.md) | **Detect at the edge, translate at the seam, decide where the context is.** Every `catch` must name a decision; a handler that only logs and continues, or re-raises unchanged, is a misplacement. Tells: `except Exception: log(e)` in a service; `if "duplicate key" in str(exc)` at a controller — string-matching a driver's message instead of an error type at the seam; a validator called from twelve leaves because the value was never made safe where it entered; a lower layer's exception type in a public signature; `raise X()` without `from`, losing the cause. Count the seams between throw and catch: more than one means nobody translated |
| [Complete Mediation](reliability/complete-mediation.md) | **A cross-cutting rule that each call site must remember to apply**, where the rule is the authority to act (a permission, a lock or lease, its freshness), is missing at the site that forgot, and nothing fails. Repair by design: the one door every change passes (the store, the repository) checks under the lock its write takes and returns the only handle that can write (the open transaction), closed on exit, resolving child resources through itself; each exemption is its own narrow operation. This removes forgetting by honest authors; database privileges stop bypass. Tells (structural): a write door that accepts a caller with no proof of the check; the check appears N times and the members (the route table, the handler registry) number M > N; independent decisions of one rule with different meanings; a fix that adds the check to one more site; a refusal with no record. The **population census** (`readings/auditing.md`) detects the holes; it is never the repair |
| [Resilience & Graceful Degradation](reliability/resilience.md) | Retry, fall back, circuit-break; design for partial failure |
| [Liveness: Every State Has an Owner](reliability/liveness.md) | Every state leaves by itself or names the person and decision it waits for; an unowned state gets an owner by accident (a Retry button, a runbook, a repairing guard, a sweep that fails it) |
| [Principle of Least Privilege](reliability/least-privilege.md) | Minimum permissions per component |

## Maintainability & Operations

*Code is a living artifact. The Boy Scout Rule keeps code improving incrementally with every change, while Observability & Transparency ensure you can understand what your systems are doing in production.*

| Principle | What it says |
|-------------|----------------|
| [Boy Scout Rule](reliability/boy-scout-rule.md) | Leave code better than you found it, scoped to what you touch |
| [Observability & Transparency](reliability/observability.md) | Structured telemetry as your production debugger |
