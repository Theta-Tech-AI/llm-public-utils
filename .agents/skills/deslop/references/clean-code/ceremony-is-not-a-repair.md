---
name: deslop-clean-code-ceremony-is-not-a-repair
description: Deslop principle — Ceremony Is Not a Repair: added machinery that duplicates a contract the code already owns changes nothing, and converts an automatic mechanism into a manual obligation nobody enforces.
---

# Ceremony Is Not a Repair

> "This is a perfect example of the type of change AI will happily make. It does literally nothing and makes the
> code worse."
> — a Go diff posted publicly, in which three hunks of hygiene were read as improvement

A diff can read as hygiene and own nothing. The lifetime of the background goroutine in this example already has
an owner: the `ctx` the function is handed. Go's cancellation contract *is* that context — cancel it and the
goroutine's `case <-ctx.Done()` returns. The change adds a **second** owner for the same lifecycle: a derived
cancellable context, a `done` channel, and a cleanup closure returned to the caller. Ownership is now ambiguous,
and the added owner is the **manual** one: the caller must remember to call `return`'s closure, and nothing —
neither the type system nor a test — enforces it.

```go
// ❌ a second handle for a lifecycle that already had one
func cycleStatusMessages(
	ctx context.Context,
	logger *slog.Logger,
	res responseSender,
	interval time.Duration,
	options []string,
) func() {                                  // <- the new obligation
	ctx, cancel := context.WithCancel(ctx)  // <- second owner
	tick := time.NewTicker(interval)
	done := make(chan struct{})
	go func() {
		defer close(done)
		defer tick.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-tick.C:
				if err := res.Send(next(options)); err != nil {
					logger.WarnContext(ctx, "send failed", "err", err)
				}
			}
		}
	}()
	return func() { cancel(); <-done }       // <- unbounded wait, dropped by the first caller that forgets
}

// ✅ keep the two hunks that are real, delete the third
func cycleStatusMessages(
	ctx context.Context,
	logger *slog.Logger,
	res responseSender,     // narrowed to an interface: testability, real
	interval time.Duration,
	options []string,
) {
	tick := time.NewTicker(interval)   // real only on Go < 1.23 — see below
	if err := res.Send(next(options)); err != nil {
		logger.WarnContext(ctx, "send failed", "err", err)
	}
	go func() {
		defer tick.Stop()
		for {
			select {
			case <-ctx.Done():   // the owner the caller already has
				return
			case <-tick.C:
				if err := res.Send(next(options)); err != nil {
					logger.WarnContext(ctx, "send failed", "err", err)
				}
			}
		}
	}()
}
```

**Delete every added line and the behaviour of the function is identical** — same sends, same exit condition, same
telemetry. What changed is the contract: the function grew a return value that its callers may ignore, and a
cleanup path that blocks on `<-done` for as long as a network send takes, which the original never did.

## The diff is not one thing — classify its hunks

The reason this lands is that it travels with real work. Three hunks, three kinds:

| Hunk | Kind | Verdict |
|---|---|---|
| `*connect.ServerStream[T]` → a narrow `responseSender` interface | API / testability | **real** — take it |
| `time.Tick` → `time.NewTicker` + `defer tick.Stop()` | behaviour | **real on Go < 1.23**; **a no-op from Go 1.23**, which made unstopped tickers garbage-collectable when unreferenced ("The Go 1.23 implementation avoids resource leaks in programs that don't use `t.Stop`") |
| `context.WithCancel` + `done` + returned cleanup | ceremony | **delete it** — no behaviour change, a new unenforced duty, a new unbounded wait |

A mixed diff is read as one thing, and the ceremony inherits the credibility of the genuine fix beside it. That is
the mechanism by which a no-op arrives on `main`: nobody approved it, everybody approved its neighbours.

## The tests

Run them in this order; the first two usually settle it.

1. **Delete test** — remove every added line and run the suite. Identical results mean ceremony. Do this by
   running it, not by reasoning about it: the point of the test is that a no-op *cannot fail*, so only execution
   distinguishes "harmless" from "load-bearing".
2. **Existing-owner test** — name the mechanism already in the signature or the call site that covers this concern:
   a `ctx`, an error return, a schema, a retry client, a transaction, a typed budget. If one exists, an added
   second mechanism must justify itself *against* that owner, not merely beside it.
3. **Automation-direction test** — does the change convert an automatic mechanism into a manual one? `defer`, a
   context, an interface and a returned error are enforced by scope, by the runtime or by the compiler; a returned
   cleanup closure is enforced by politeness. Hygiene moves toward automation. A change that inverts the direction
   is not hygiene, whatever it is called.
4. **Obligation test** — does it create a duty on every caller that the compiler cannot check? Count the call sites;
   each is a place the duty can be dropped, and one dropped call leaves the new machinery strictly worse than
   absent (a derived context never cancelled, a ticker never stopped, a wait never performed).
5. **Bundling test** — classify each hunk as behaviour, API, or ceremony, and refuse to review them as one unit. If
   a diff cannot be described without the word "also", the ceremony is riding in.
6. **Signature-return test** — a function that ends `return func() { … }` while already receiving a context, a
   stream, a logger or a handle is a candidate on sight: the returned closure is the second lifecycle handle.

## The family: one concern, many second owners

| Added mechanism | The owner it duplicates | Where the concern enters |
|---|---|---|
| derived `context.WithCancel` + returned `cancel()` | the `ctx` parameter | the caller's context tree |
| `done` channel + `<-done` in a cleanup | `ctx.Done()`, already in the `select` | the same context tree |
| hand-rolled retry loop | the retry client the call already passes through | the HTTP/DB client |
| re-validating a value the parser already proved | the parse boundary's return type | the edge |
| ad-hoc counters guarding a size or budget | the budget type the factory receives | configuration |
| a second logger threaded beside the contextual one | the logger already derived from the request | request scope |
| an explicit lock guarding state inside a transaction | the transaction's isolation | the data layer |

The common shape: the concern is *already owned*, the owner is *automatic*, and the change adds a parallel owner
that is *manual*. Each of these is the same finding under a different noun.

## The repair

**Delete the ceremony. If a hygiene gap is real, repair the existing owner — never add a second one.**

- Keep the hunks that change behaviour or narrow an API; drop the ones that only add a handle.
- If the caller genuinely needs to know the goroutine has stopped, that is a decision for the seam that *owns* the
  goroutine — the function that started it, using `errgroup`/`WaitGroup` — not a closure handed to every caller.
- If the derived context is genuinely needed (the function must cancel its own work independently), `defer
  cancel()` inside it, or return the cancel func with a contract the call sites cannot ignore and a `go vet`
  (`lostcancel`) clean run. A cancel func returned and dropped is the leak the analyser exists to catch; returning
  it inside another closure is how that warning is evaded.
- Prove the need with a test that fails before the change. A hygiene hunk with no failing test behind it is a
  belief.

## Boundaries

This is not "no cleanup funcs" and not "no contexts":

- **Returning a closer is the idiom when the function creates the resource and receives no owner** — `os.Open` →
  `defer f.Close()` is correct, because nothing else in the signature names that resource's lifetime.
- **A function that must cancel independently may derive a context**, provided the cancel is `defer`red in the
  function that derived it, or returned with an unavoidable contract.
- **Interface narrowing is always welcome.** Do not let this principle block a testability change; it targets the
  hunk that adds a handle, not the hunk that removes a concrete type.
- **A compatibility fix on an old runtime is real work.** The ticker hunk above is a genuine leak fix before Go
  1.23 and a no-op after it — the finding is that nobody checked which era the code lives in.

## Prior art

| Term | Source | How it relates |
|---|---|---|
| **Cargo-cult programming** | folklore; Wikipedia | Ceremony copied in form without the reason that made it necessary. This principle is the change-level detector for it. |
| **Accidental complexity** | Fred Brooks, *No Silver Bullet* (1986) | The added machinery is accidental, not essential: it costs reading and maintenance and buys no behaviour. |
| **`lostcancel` analyser** | `golang.org/x/tools/go/analysis/passes/lostcancel` | Already fails a build when a cancel func is discarded — the shape in this principle is the same defect with an extra closure in between, which the analyser cannot see. |
| **Go 1.23 timer changes** | Go Wiki, *Go 1.23 Timer Channel Changes* | Unstopped tickers that are unreferenced are now garbage-collectable, so "replace `Tick` with `NewTicker`" is redundant on current Go. |

**What this library adds:** the framing — a second mechanism is an ownership defect rather than "unnecessary
code" — plus the six tests above, the hunk classification (behaviour / API / ceremony), and the rule that the
repair of a hygiene gap is to strengthen the existing owner, never to add a parallel one.

## Relation to other principles

| Principle | Relationship |
|---|---|
| [**Patchwork**](patchwork.md) | The same disease one revision earlier: compensating code that already exists. This names the compensating code a *change* adds. |
| [**Design by Contract**](../reliability/design-by-contract.md) | Supplies the vocabulary for the fault: the change weakens the contract (an optional duty) while appearing to strengthen it. |
| [**No Silent Defaults**](../reliability/no-silent-defaults.md) | A caller that ignores the returned closure gets the old behaviour silently — the duty is a default, and the default is "skip it". |
| [**DRY**](../architecture/dry.md) | The duplicate here is a *mechanism*, not a line: one concern, two implementations, only one of them enforced. |
| [**One Logical Unit, One Home**](../architecture/one-logical-unit-one-home.md) | That principle gives a scattered unit one home; this one refuses a second home for something that already has one. |
| [**KISS**](kiss.md) | The added structure is complexity with no corresponding capability. |
| [**YAGNI**](yagni.md) | "Deterministic shutdown" is built for a caller that does not exist; the existing caller cancels its context. |
| [**Decide, Don't Cope**](decide-dont-cope.md) | The change copes with an imagined shutdown problem instead of deciding who owns the goroutine. |

## Summary

1. **Added machinery for an already-owned concern changes nothing** — the concern had an owner (the context, the
   client, the schema, the transaction); a second owner makes ownership ambiguous without adding behaviour.
2. **Direction decides whether it is hygiene.** Automatic mechanisms become manual obligations: scope, runtime and
   compiler enforcement are traded for a caller remembering. Hygiene moves the other way.
3. **A new unenforced duty makes the code worse than the code it replaced.** The first caller that ignores the
   returned handle leaves the derived context uncancelled and the leak in place — with the added ceremony on top.
4. **Classify the hunks: behaviour, API, ceremony.** A no-op rides in on a real fix because the diff is reviewed as
   one thing; the ceremony inherits the credibility of its neighbour.
5. **Repair the owner, never add a parallel mechanism.** If the gap is real, the fix belongs at the seam that owns
   the resource, and it must come with a test that fails before it.
