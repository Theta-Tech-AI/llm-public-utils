---
name: deslop-clean-code-least-surprise
description: Deslop principle — Principle of Least Surprise: Components behave the way users expect.
---

# Principle of Least Surprise

> "In interface design, always do the least surprising thing."
> — Eric S. Raymond

Components should behave the way users expect. Separate state-changing commands from queries, make names match behavior, return consistent types from similar methods, choose sensible defaults, and never hide side effects the signature doesn't imply. The usual surprises: methods whose names imply a query but secretly mutate, non-standard parameter order, inconsistent error handling across sibling methods, and "spooky action at a distance" where one call perturbs something unrelated. If you can't name a thing accurately, the design — not the name — is probably wrong.
