---
name: deslop-architecture-convention-over-configuration
description: Deslop principle — Convention Over Configuration: Sensible defaults with escape hatches.
---

# Convention Over Configuration

> "You're not a beautiful and unique snowflake. By giving up vain individuality, you can leapfrog the toils of mundane decisions, and make faster progress in areas that really matter."
> — David Heinemeier Hansson, The Rails Doctrine

Provide sensible defaults that work out of the box, and require explicit configuration only when deviating from the norm. Most decisions aren't worth making — if 90% use `id` as the primary key, don't force everyone to specify it. Rails turns a `User` class into a `users` table with a `user_id` foreign key automatically; Django, Spring Boot, Next.js routing, and pytest test discovery all work the same way, each with an escape hatch (`self.table_name = "legacy_accounts"`) for the cases that differ.

```python
# ❌ Wrong - Forcing configuration for obvious defaults
service = UserService(
    table_name="users",
    id_column="id",
    created_at_column="created_at",
    updated_at_column="updated_at",
)

# ✅ Correct - Sensible defaults with escape hatches
class UserService:
    def __init__(self, table_name: str = "users", id_column: str = "id"):
        self.table_name = table_name
        self.id_column = id_column

service = UserService()                              # Zero config for the common case
legacy = UserService(table_name="legacy_accounts")  # Override only what differs
```

The cost is hidden magic: implicit behavior is harder to debug, you must learn the convention before you can deviate, and convention-optimized common cases can fight you at the edges (a legacy DB named `tbl_usr_accounts` means fighting the framework). This is why Python prizes "explicit over implicit" — the resolution is that conventions must be *discoverable* and well documented. Convention serves you until it doesn't; then configure explicitly.
