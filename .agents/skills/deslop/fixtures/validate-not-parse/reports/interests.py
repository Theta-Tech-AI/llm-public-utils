from collections import Counter

from profile import store


def interest_counts(user_ids: list[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for user_id in user_ids:
        interests = store.get(user_id).get("interests") or []
        counts.update(sorted(set(interests)))
    return counts
