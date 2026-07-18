---
name: deslop-reliability-least-privilege
description: Deslop principle — Principle of Least Privilege: Minimum permissions per component.
---

# Principle of Least Privilege

> "Every program and every user of the system should operate using the least set of privileges necessary to complete the job."
> — Jerome Saltzer, *Protection and the Control of Information Sharing in Multics* (1974)

Every component should run with the minimum permissions its job requires — nothing more. Fewer permissions mean fewer entry points (smaller attack surface) and less damage when a breach happens (smaller blast radius); most breaches start with a privileged credential being abused, as Equifax (permissive DB access, no segmentation) and Target (an over-privileged HVAC vendor) both showed. The principle applies at every level: a config-reading function shouldn't have write access, a read path shouldn't hold a connection with `DROP TABLE`, a payment service shouldn't reach user profiles, and an IAM policy shouldn't say `Action: "s3:*", Resource: "*"`.

```python
# ❌ Wrong - Function accepts overly broad context
def send_notification(user: User, db: DatabaseAdmin):
    email = db.query(f"SELECT email FROM users WHERE id = {user.id}")
    # db could delete the entire users table!

# ✅ Correct - Function receives only what it needs
def send_notification(email: str):
    send_email(email, "Your notification...")  # Cannot touch the database
```

Default to deny and grant explicitly, separate credentials by function (read vs. write), time-bound elevated access, and audit regularly — permissions accumulate as roles change and "temporary" access becomes permanent. Watch for the verbal tells: "just give it admin, it's easier," "we'll lock it down later," "it needs that for debugging." Least privilege partners with Zero Trust: Zero Trust authenticates *who* is making a request, PoLP limits what that authenticated identity can *do*.
