# GitHub closure metrics runbook

Optional adapter: how to run the packaged script for milestone timeline data, and what its numbers do and do not prove.

## Optional GitHub adapter

Use `scripts/closure_metrics.py --help` for a read-only snapshot from authenticated `gh` or a saved fixture. It queries current milestone members and their close/reopen timeline events. It does not mutate issues, infer model identity, establish historical membership, or measure review wait without stage timestamps. Its unit tests ship beside it and need no network or credentials — from this skill's directory run `python3 -m unittest discover -s tests`.

Keep collected repository names, titles, identities, and event data outside the skill package. The reusable skill should contain instructions and synthetic examples, not a private campaign's records.

---

Related: [measurement](measurement.md)
