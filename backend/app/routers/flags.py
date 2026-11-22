from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.db import get_db
from datetime import datetime, timezone

from app.models import Flag, Project, Rule, ScheduledChange
from app.services.schedule import apply_due_changes, parse_apply_at

router = APIRouter()


class FlagIn(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    description: str = ""
    enabled: bool = False
    rollout_percent: int = Field(default=0, ge=0, le=100)


def as_json(flag: Flag, rules: list[Rule]) -> dict:
    return {
        "id": flag.id,
        "key": flag.key,
        "description": flag.description,
        "enabled": flag.enabled,
        "rollout": flag.rollout_percent,
        "updated_at": flag.updated_at.isoformat(),
        "rules": [
            {
                "attribute": rule.attribute,
                "operator": rule.operator,
                "value": rule.value,
            }
            for rule in sorted(rules, key=lambda r: r.position)
        ],
    }


async def rules_for(db: AsyncSession, flag_id: int) -> list[Rule]:
    result = await db.execute(select(Rule).where(Rule.flag_id == flag_id))
    return list(result.scalars().all())


@router.get("/{project_key}/flags")
async def list_flags(project_key: str, db: AsyncSession = Depends(get_db)):
    project = await db.scalar(select(Project).where(Project.key == project_key))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(select(Flag).where(Flag.project_id == project.id))
    flags = list(result.scalars().all())

    return [as_json(flag, await rules_for(db, flag.id)) for flag in flags]


@router.post("/{project_key}/flags", dependencies=[Depends(require_admin)])
async def create_flag(
    project_key: str, body: FlagIn, db: AsyncSession = Depends(get_db)
):
    project = await db.scalar(select(Project).where(Project.key == project_key))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    existing = await db.scalar(
        select(Flag).where(Flag.project_id == project.id, Flag.key == body.key)
    )
    if existing:
        raise HTTPException(status_code=409, detail="That flag key already exists")

    flag = Flag(
        project_id=project.id,
        key=body.key,
        description=body.description,
        enabled=body.enabled,
        rollout_percent=body.rollout_percent,
    )
    db.add(flag)
    await db.commit()
    await db.refresh(flag)

    return as_json(flag, [])


class ScheduleIn(BaseModel):
    apply_at: str
    ramp_to: int = Field(ge=0, le=100)
    ramp_minutes: int = 0


@router.post("/{project_key}/flags/{flag_key}/schedule")
async def schedule_change(
    project_key: str,
    flag_key: str,
    body: ScheduleIn,
    db: AsyncSession = Depends(get_db),
):
    """Queue a rollout change for later, optionally ramping towards it."""
    flag = await db.scalar(select(Flag).where(Flag.key == flag_key))
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    change = ScheduledChange(
        flag_id=flag.id,
        apply_at=parse_apply_at(body.apply_at),
        ramp_to=body.ramp_to,
        ramp_minutes=body.ramp_minutes,
    )
    db.add(change)
    await db.commit()
    await db.refresh(change)

    return {"id": change.id, "apply_at": change.apply_at.isoformat()}


@router.post("/{project_key}/flags/tick", dependencies=[Depends(require_admin)])
async def tick(project_key: str, db: AsyncSession = Depends(get_db)):
    """Apply whatever has come due. Called by the scheduler worker."""
    applied = await apply_due_changes(db, datetime.now(timezone.utc))
    return {"applied": applied}
