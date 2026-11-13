import hashlib

BUCKETS = 10_000


def bucket_for(flag_key: str, user_key: str) -> int:
    """Which of 10,000 buckets this user falls into for this flag.

    Hashed with the flag key so a user is not in the same bucket for every
    flag, which would make a 10% rollout always hit the same tenth.
    """
    digest = hashlib.sha256(f"{flag_key}:{user_key}".encode()).hexdigest()
    return int(digest[:8], 16) % BUCKETS


def in_rollout(flag_key: str, user_key: str, percent: int) -> bool:
    if percent <= 0:
        return False
    if percent >= 100:
        return True
    return bucket_for(flag_key, user_key) < percent * BUCKETS // 100
