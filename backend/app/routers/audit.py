import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Flag, FlagChange, Project
from app.services.audit import history_for, summarise

logger = logging.getLogger(__name__)

router = APIRouter()


def as_json(change: FlagChange, flag_key: str) -> dict:
    return {
        "id": change.id,
        "flag_key": flag_key,
        "version": change.version,
        "field": change.field,
        "before": change.before,
        "after": change.after,
        "actor": change.actor,
        "note": change.note,
        "changed_at": change.changed_at.isoformat(),
    }


@router.get("/{project_key}/history")
async def project_history(project_key: str, db: AsyncSession = Depends(get_db)):
    """Every recorded change across a project's flags, newest first."""
    project = await db.scalar(select(Project).where(Project.key == project_key))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(FlagChange)
        .join(Flag, Flag.id == FlagChange.flag_id)
        .where(Flag.project_id == project.id)
        .order_by(FlagChange.changed_at.desc())
    )
    changes = list(result.scalars().all())

    entries = []
    for change in changes:
        flag = await db.scalar(select(Flag).where(Flag.id == change.flag_id))
        entries.append(as_json(change, flag.key))

    return {"summary": summarise(changes), "changes": entries}


@router.get("/{project_key}/flags/{flag_key}/history")
async def flag_history(
    project_key: str,
    flag_key: str,
    limit: int | None = Query(default=None),
    since: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """One flag's history, optionally trimmed by count or by date."""
    project = await db.scalar(select(Project).where(Project.key == project_key))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    flag = await db.scalar(
        select(Flag).where(Flag.project_id == project.id, Flag.key == flag_key)
    )
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    try:
        changes = await history_for(db, flag.id, limit=limit, since=since)
    except Exception:
        # Worth a line in the log before it becomes a 500 somewhere else.
        logger.exception("history lookup failed for %s/%s", project_key, flag_key)
        raise

    return {
        "summary": summarise(changes),
        "changes": [as_json(change, flag.key) for change in changes],
    }
