---
name: deslop-reliability
description: Deslop principles, Part III: Reliability — Fail-Fast, Design by Contract, Postel's Law, Resilience & Graceful Degradation, Least Privilege, Boy Scout Rule, Observability.
---

# Part III: Reliability

> *Building robust, maintainable systems. These principles govern how code handles errors, maintains itself over time, and operates in production.*

Each principle is a self-contained file; read every file when auditing this layer.

## Robustness & Safety

*How does code handle the unexpected? Fail-Fast detects errors early, Design by Contract makes expectations explicit, Postel's Law enables interoperability, Resilience keeps systems running despite failures, and Principle of Least Privilege limits damage from breaches.*

| Principle | What it says |
|-------------|----------------|
| [Fail-Fast & Defensive Programming](reliability/fail-fast.md) | Detect and report errors at the earliest possible moment |
| [Design by Contract](reliability/design-by-contract.md) | Explicit preconditions, postconditions, invariants |
| [Postel's Law (Robustness Principle)](reliability/postels-law.md) | Strict output, tolerant input; paranoid at security boundaries |
| [Resilience & Graceful Degradation](reliability/resilience.md) | Retry, fall back, circuit-break; design for partial failure |
| [Principle of Least Privilege](reliability/least-privilege.md) | Minimum permissions per component |

## Maintainability & Operations

*Code is a living artifact. The Boy Scout Rule keeps code improving incrementally with every change, while Observability & Transparency ensure you can understand what your systems are doing in production.*

| Principle | What it says |
|-------------|----------------|
| [Boy Scout Rule](reliability/boy-scout-rule.md) | Leave code better than you found it, scoped to what you touch |
| [Observability & Transparency](reliability/observability.md) | Structured telemetry as your production debugger |
