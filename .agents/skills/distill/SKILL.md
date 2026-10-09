---
name: distill
description: Separate code between an upstream framework and downstream overlays in both directions — send provider-agnostic distillate upstream, pull owned deliverables back, and adopt downstream distillate into upstream. Use when deduplicating overlay code, auditing a downstream, or deciding where a fix belongs.
---

# /distill

Every overlay file is recopied and re-merged on each upstream bump. Distillation puts each line in the repo that owns it.

- **Distillate** rises upstream: fixes, refactors, Protocols, and types any other downstream would want.
- **Residue** stays in the overlay: SDK calls, identity, tenants, branding, domain content, retention and audit policy.

## Ownership gate

Ownership beats shape. A contracted deliverable, a proprietary feature, or the domain logic the consumer exists to own is residue even when byte-identical to upstream. Being identical means the boundary was breached: pull it back and delete it upstream, DDL included. Low diffs and "looks generic" push code up, so an uncertain file stays in the consumer repo. Upstreaming needs one sentence: this is generic platform IP the framework owns.

## Passes

- **Forward** — overlay to upstream, when a generic fix sits in the overlay.
- **Reverse** — upstream to overlay, when owned code is found there.
- **Adoption** — read a downstream overlay for distillate; never commit to it.

The gate decides. Pause on a shared-file bug, deploy fix, review, generic doc, missing counterpart, or policy on a seam.

## Decision

First yes wins.

1. Owned, proprietary, or domain-defining? Residue. Already upstream? Pull it back.
2. Provider SDK, identity, or branding? Residue.
3. Client data, domain rules, tenants, or project-only policy? Residue, or distill only the abstraction.
4. New Protocol, factory, or hook? Distillate the contract; residue the implementation.
5. Depends on a consumer type or error? Land a neutral upstream type, map it in the overlay, walk again.
6. Would any other downstream want this equally? Distillate.
7. Otherwise residue.

The overlay imports upstream; upstream never imports the overlay. Inject a consumer shape through a parameter, Protocol, or resolver.

Under 15% diff (over 40 lines) or byte-identical after `git clean -fd` is redundancy, not ownership. Past ~250 frontend or ~400 backend lines with the diff in one or two spots, split upstream first. Distill a seam's missing half; leave the domain. De-brand playbooks; product and compliance docs stay residue.

## Procedure

Never commit another agent's upstream work. If the submodule lags the branch it tracks, bump and re-audit.

**Forward.** Commit a compiling baseline. Audit near-copies and overlay-only files with no domain terms; tests move with the behavior. Ship a regression test, split god-files, and strip names, contract ids, issue numbers, and staging stories. Wait for a mirror SHA when one feeds the submodule. Bump only to a superset (`merge-base --is-ancestor` of the old SHA). Shrink the overlay only when `git show` of the pristine file matches — rsync first makes `cmp` true by construction. Rebuild downstream.

**Reverse.** Scan for brand, tenant, contract, and domain hits, and for imports that exist only via the overlay. Port every upstream-only bit and prove the pin plus overlay builds before deleting those files and tests.

**Adoption.** Pass the one-sentence test or leave it. Generic module plus tests, no downstream defaults. The downstream drops its copy on the next bump.

Refuse a twin overlay unless that commit tracks an upstream issue and the twin dies when it lands; defaults shipped with the abstraction; a deliverable moved upstream; a test left behind; upstream removed first; a rejected shape kept.

Done when forward cuts overlay lines, reverse drives brand and contract hits toward zero, or adoption drops the duplicate. Otherwise you only moved code.

`/shatter` splits a file first. When `/deslop` flags overlay files, run this gate.
