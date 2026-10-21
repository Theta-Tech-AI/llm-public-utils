---
name: deslop-clean-code-unclaimed-guarantee
description: Deslop principle — An Unclaimed Guarantee: added machinery that promises a real capability no caller claims, beside an owner that already covers what callers use, is ceremony — and an optional duty nobody enforces is worse than none.
---

# An Unclaimed Guarantee

> "This is a perfect example of the type of change AI will happily make. It does literally nothing and makes the
> code worse."
> — a Go diff posted publicly, in which three hunks of hygiene were read as improvement

The honest reading of the motivating diff is subtler than "it does nothing", and the difference is the whole
principle. The change *does* add two real capabilities:

- **independent cancellation** of this worker, scoped to the function rather than inherited from the caller's tree;
- **completion synchronisation** — the returned closure blocks until the goroutine's loop and deferred cleanup
  finish, which a parent context does **not** provide. A context signals cancellation; it never establishes that
  work has stopped.

So the finding is not redundancy. It is that **nothing claims those guarantees**: the caller cancels its context,
which was already sufficient for every call site; the wait is never observed; and the *only* new obligation —
call the returned closure — is unenforced by the compiler and by every test. What the diff adds is a promise
nobody asked for, on top of an owner that already covers what callers actually use, plus a blocking wait on a
`Send` that receives no cancellation at all.

```go
// ❌ a second handle whose guarantees no caller claims
func (s *Service) CycleStatus(
	ctx context.Context,
	res Sender,
	interval time.Duration,
	options []string,
) func() {                                  // <- the unenforced duty
	ctx, cancel := context.WithCancel(ctx)  // <- independent cancellation …
	tick := time.NewTicker(interval)
	done := make(chan struct{})
	if err := res.Send(first(options)); err != nil {
		s.Log.WarnContext(ctx, "send failed", "err", err)
	}
	go func() {
		defer close(done)                   // … and completion sync
		defer tick.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-tick.C:
				if err := res.Send(next(options)); err != nil {
					s.Log.WarnContext(ctx, "send failed", "err", err)
				}
			}
		}
	}()
	return func() { cancel(); <-done }       // <- blocks on a send nobody can cancel
}

// ✅ the same function minus the unclaimed guarantees
func (s *Service) CycleStatus(
	ctx context.Context,
	res Sender,          // narrowed to an interface: a real change, keep it
	interval time.Duration,
	options []string,
) {
	tick := time.NewTicker(interval)
	defer tick.Stop()
	if err := res.Send(first(options)); err != nil {
		s.Log.WarnContext(ctx, "send failed", "err", err)
	}
	go func() {
		for {
			select {
			case <-ctx.Done():   // the owner the caller already has
				return
			case <-tick.C:
				if err := res.Send(next(options)); err != nil {
					s.Log.WarnContext(ctx, "send failed", "err", err)
				}
			}
		}
	}()
}
```

The pair above differs **only** in the trio: same initial send, same loop, same telemetry. That is the controlled
comparison the rule needs — a pair that also changes the send path proves nothing about the trio.

## What the diff actually contains — classify the hunks

| Hunk | Kind | Verdict |
|---|---|---|
| `*connect.ServerStream[T]` → a narrow sender interface | API / testability | **real** — take it |
| `time.Tick` → `time.NewTicker` + `defer Stop()` | behaviour, conditionally | **real before Go 1.23**; from Go 1.23 the *garbage-collection* reason disappears, because unreferenced unstopped tickers become collectable — but a referenced ticker may still need stopping, so this is a judgement about the call site, not an automatic redundancy |
| `context.WithCancel` + `done` + returned cleanup | guarantee, unclaimed | **delete, or claim it** — see the tests |

A no-op or near-no-op rides in on real work because the diff is reviewed as one thing. Ask for the guarantee, the
caller that claims it, and nothing else.

## The tests — review prompts with a contract each

1. **Guarantee naming** — state, in caller-visible terms, what the added machinery promises: completion,
   ordering, exclusivity, retry, scope of cancellation. If you cannot name it, it is decoration.
2. **Claimed-by-a-caller** — find the caller whose code would be **wrong** without that guarantee: a line that
   waits, a branch that depends on completion, a test that asserts shutdown ordering. No such line, no finding is
   justified — and this is the decisive, decidable test in a closed repository: grep the call sites.
3. **Enforcement** — how is the guarantee honoured if a caller forgets? Compile error, panic, or politeness. An
   optional duty is not a contract, and each unenforced call site is a place the guarantee silently lapses; say how
   many there are.
4. **Owner** — what does the existing owner (context, client, schema, transaction) already guarantee? Add only what
   it cannot, and say which capability the owner lacks.
5. **Hunk classification** — behaviour / API / guarantee / ceremony, per hunk. A PR body that cannot describe the
   diff without the word "also" is carrying something unclaimed; make the author name the guarantee and the caller.
6. **Signature-return as a prompt, not a verdict** — a function ending `return func() { … }` while already
   receiving a context is *worth a look*, and nothing more: returning a cleanup handle is idiomatic Go
   (`os.Open`, `context.AfterFunc(ctx, f)`, subscription unsubscribe). The question is always whether a caller
   claims it.

**None of these prove behavioural equivalence.** "Delete it and the suite still passes" shows only that no test
observed the difference; the difference may be a guarantee the suite never exercised. The delete test is a cheap
first probe, not a proof, and it must never be quoted as "it does nothing".

## The family: one concern, many second handles

| Added handle | The owner it stands beside | The guarantee it usually claims and does not get |
|---|---|---|
| derived `WithCancel` + returned `cancel()` | the `ctx` parameter | per-call cancellation scope — genuinely new, rarely claimed |
| `done` channel + `<-done` in a cleanup | `ctx.Done()` | completion synchronisation — new, and unenforced |
| hand-rolled retry loop | the retry client the call passes through | a retry policy — usually weaker than the client's |
| re-validating a value the parser already proved | the parse boundary's return type | nothing: the guarantee already exists |
| ad-hoc counters guarding a size or budget | the budget type the factory receives | a ceiling the type already enforces |
| a second logger threaded beside the contextual one | the logger derived from the request | nothing: no lifetime contract is involved |
| an explicit lock inside a transaction | the transaction's isolation | exclusivity the transaction already has |

## The repair

**Claim it, or delete it.** Three legitimate endings, in order of preference:

1. **Delete** when no caller claims the guarantee. The common case: the caller already cancels a context.
2. **Claim it at the seam that owns the resource** — if shutdown genuinely must be synchronous, the function that
   started the goroutine awaits it with `errgroup`/`WaitGroup`, so the guarantee is a fact of that component
   rather than a closure each caller may drop.
3. **Keep the handle and enforce it** — return it with a contract the call sites cannot ignore, `defer` the cancel
   in the function that created it, or restructure so the type makes the duty part of the API (a closer owned by a
   struct, released by `defer`). Then make the blocking wait bounded by giving `Send` a cancellation path; a
   cleanup that blocks indefinitely on a network send has traded one hazard for a worse one.

## Boundaries

- **A context plus a cleanup handle is idiomatic** — `context.AfterFunc(ctx, f)` takes a context and returns a
  stop function; subscriptions return unsubscribe closures. The finding is not the shape of the signature.
- **Parent cancellation is not replaced by the added handle.** Ignoring the closure still lets the caller's context
  terminate the worker, so "worse than none" must be argued from the *unclaimed blocking wait* and the dropped
  cancel, not from leak claims that do not hold.
- **A function may derive its own context** when it owns a lifecycle boundary, but `defer cancel()` inside the
  function that derived it cancels that worker as the function returns — so a returned cancel belongs to a
  long-lived owner, not to a fire-and-forget starter.
- **Interface narrowing is always welcome**, and a compatibility fix on an older runtime is real work. This
  principle targets the hunk that adds a handle, not the hunk that removes a concrete type.
- **A logger, a clock or a random source establishes no lifetime contract** — pairing one with a cleanup handle is
  not evidence of anything.

## Facts worth getting right (this file's first version got three of them wrong)

- **`go vet`'s `lostcancel`** is a *local use/path heuristic*: it flags a cancel func discarded (`_`) or unused on
  a path. Returning it counts as use, and the analyser does not follow callers to catch a result dropped at the
  call site. It is not enforcement of a caller obligation, and `go build` does not run vet.
- **Go 1.23 timers:** unreferenced unstopped tickers became garbage-collectable, which removes the GC reason for
  `Tick` → `NewTicker` + `Stop`. It does not make `Stop` universally redundant, and the rollout depended on module
  and compatibility settings.
- **`time.Tick(d)` returns nil for `d <= 0`, while `time.NewTicker(d)` panics** — a behavioural difference the swap
  introduces, so the swap is not free even where the leak argument does not apply.
- **A context signals cancellation; it does not wait for completion.** Cancellation and completion synchronisation
  are different guarantees, and the second one is what such diffs usually add.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| **Cargo-cult programming** | folklore; the Jargon File | Form copied without the reason. Useful as an analogy once purposelessness is established — it is not the argument itself. |
| **Accidental complexity** | Fred Brooks, *No Silver Bullet* (1986) | The machinery is difficulty incidental to implementing the software; Brooks does not claim such code changes no behaviour, and neither does this file. |
| **`lostcancel` analyser** | `golang.org/x/tools/go/analysis/passes/lostcancel` | A local heuristic on the *use* of a cancel func — not a check that callers honour a returned duty. |
| **Go 1.23 timer changes** | Go Wiki, *Go 1.23 Timer Channel Changes* | The GC fact that makes part of the motivating diff redundant on current Go, and the reason the claim must be conditional. |
| **Context vs synchronisation** | `pkg.go.dev/context`; `sync` primitives | The distinction the first version of this file missed: cancellation authority is not completion. |

**What this library proposes — and it is a heuristic, not a theorem:** the *claimed-guarantee* test (name the
guarantee, then find the caller that would be wrong without it), the enforcement question, and the hunk
classification. Treat it as a review prompt that makes an author state their case, not as a proof that a change is
empty.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Patchwork**](patchwork.md) | Compensating code that already exists. This names the compensating machinery a *change* adds, and asks who claims it. |
| [**Design by Contract**](../reliability/design-by-contract.md) | Supplies the vocabulary: an unenforced duty is not a contract, it is a hope the caller reads the docs. |
| [**No Silent Defaults**](../reliability/no-silent-defaults.md) | The caller that ignores the handle silently gets the old behaviour — the duty's default is "skip it". |
| [**DRY**](../architecture/dry.md) | The duplicate is a *guarantee*, not a line: two mechanisms, one of them unclaimed. |
| [**One Logical Unit, One Home**](../architecture/one-logical-unit-one-home.md) | That principle gives a scattered unit one home; this one asks whether a second home's guarantees are used at all. |
| [**KISS**](kiss.md) / [**YAGNI**](yagni.md) | Complexity without a claimant; a guarantee built for a caller that does not exist. |
| [**Decide, Don't Cope**](decide-dont-cope.md) | The change copes with an imagined shutdown problem instead of deciding where the lifecycle ends. |

## Summary

1. **Not "does nothing" — "guarantees something unclaimed".** The added machinery usually provides a real
   capability (completion synchronisation, per-call cancellation); the finding is that no caller claims it and
   nothing enforces it.
2. **Name the guarantee, find the claimant.** In a closed repository this is decidable: grep the call sites for the
   line that would be wrong without it, and quote it, or drop the finding.
3. **An optional duty is not a contract.** If honouring it depends on every caller remembering, count the call
   sites and say how many can drop it silently.
4. **Classify the hunks: behaviour, API, guarantee, ceremony.** A near-empty change rides in on real work because
   the diff is reviewed as one whole.
5. **Repair by claiming it — delete, move it to the owning seam, or enforce it.** A blocking cleanup whose work
   cannot be cancelled has traded one hazard for a worse one, and that trade is the author's to justify.
