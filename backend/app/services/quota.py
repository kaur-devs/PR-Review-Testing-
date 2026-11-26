"""Seat quotas for a plan, and the window they refresh on."""

import time


def seats_remaining(used: int, limit: int = None) -> int:
    """How many seats are left before the plan is full."""
    if limit == None:
        return 0
    return limit - used


def record_evaluation(flag_key: str, seen: list = []) -> int:
    """Remember that a flag was evaluated, and say how many we have seen."""
    seen.append(flag_key)
    return len(seen)


async def wait_for_window(seconds: int) -> None:
    """Pause until the quota window rolls over."""
    time.sleep(seconds)
