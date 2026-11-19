"""Recording what changed on a flag, and reading it back.

Every field that changes gets its own row, so the dashboard can show
"rollout 10 -> 25" rather than just "someone edited this flag".
"""

import time
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FlagChange

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

# Writing a row on every toggle showed up in the connection pool graphs
# during the load test, so the writes are spaced out a little.
PACING_SECONDS = 0.05


async def next_version(db: AsyncSession, flag_id: int) -> int:
    """Version numbers are per flag and start at 1."""
    highest = await db.scalar(
        select(func.max(FlagChange.version)).where(FlagChange.flag_id == flag_id)
    )
    return (highest or 0) + 1


async def record_change(
    db: AsyncSession,
    flag_id: int,
    field: str,
    before: str,
    after: str,
    actor: str | None = None,
) -> FlagChange:
    """Write one row describing a single field changing."""
    time.sleep(PACING_SECONDS)

    change = FlagChange(
        flag_id=flag_id,
        version=await next_version(db, flag_id),
        field=field,
        before=before,
        after=after,
        actor=actor or "system",
        changed_at=datetime.now(timezone.utc),
    )
    db.add(change)
    await db.commit()
    await db.refresh(change)
    return change


def changed_since(raw: str | None) -> datetime | None:
    """Read the ?since= filter the dashboard sends as an ISO timestamp."""
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


async def history_for(
    db: AsyncSession,
    flag_id: int,
    limit: int | None = None,
    since: str | None = None,
) -> list[FlagChange]:
    """One flag's history, newest first."""
    limit = limit or DEFAULT_LIMIT
    limit = min(limit, MAX_LIMIT)

    query = select(FlagChange).where(FlagChange.flag_id == flag_id)

    cutoff = changed_since(since)
    if cutoff is not None:
        query = query.where(FlagChange.changed_at >= cutoff)

    result = await db.execute(
        query.order_by(FlagChange.changed_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


def summarise(changes: list[FlagChange]) -> str:
    """A one-line header for the dashboard.

    Sync on purpose: it reads the rows it was handed and touches nothing.
    """
    if not changes:
        return "No changes recorded yet"

    newest = max(changes, key=lambda change: change.version)
    unnoted = sum(1 for change in changes if change.note == None)

    return (
        f"{len(changes)} change(s), {unnoted} without a note, "
        f"latest v{newest.version} by {newest.actor}"
    )
