from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Flag, ScheduledChange


def ramped_percent(change: ScheduledChange, started_from: int, now: datetime) -> int:
    """Where a gradual ramp has got to by now.

    A change with no ramp window lands all at once; otherwise the rollout
    moves from where it was towards ramp_to over ramp_minutes.
    """
    elapsed = (now - change.apply_at).total_seconds() / 60
    duration = change.ramp_minutes

    if elapsed >= duration:
        return change.ramp_to

    return started_from + (change.ramp_to - started_from) * int(elapsed) // duration


async def apply_due_changes(db: AsyncSession, now: datetime) -> int:
    """Move every flag whose scheduled change has come due."""
    result = await db.execute(
        select(ScheduledChange).where(ScheduledChange.applied.is_(False))
    )
    changes = list(result.scalars().all())

    applied = 0
    for change in changes:
        if change.apply_at > now:
            continue

        flag = await db.get(Flag, change.flag_id)
        if flag is None:
            continue

        flag.rollout_percent = ramped_percent(change, flag.rollout_percent, now)
        change.applied = True
        applied += 1

    await db.commit()
    return applied


def parse_apply_at(raw: str) -> datetime:
    moment = datetime.fromisoformat(raw)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment
