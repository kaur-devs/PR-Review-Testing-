from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.db import get_db
from app.models import Flag, Project, Rule
from app.services.audit import record_change

router = APIRouter()


class FlagIn(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    description: str = ""
    enabled: bool = False
    rollout_percent: int = Field(default=0, ge=0, le=100)


class FlagUpdate(BaseModel):
    description: str | None = None
    enabled: bool | None = None
    rollout_percent: int | None = Field(default=None, ge=0, le=100)


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


@router.patch("/{project_key}/flags/{flag_key}")
async def update_flag(
    project_key: str,
    flag_key: str,
    body: FlagUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Change a flag, writing one history row per field that moved."""
    flag = await db.scalar(select(Flag).where(Flag.key == flag_key))
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    wanted = body.model_dump(exclude_none=True)
    for field, after in wanted.items():
        before = getattr(flag, field)
        if before == after:
            continue
        setattr(flag, field, after)
        await record_change(db, flag.id, field, str(before), str(after))

    await db.commit()
    await db.refresh(flag)

    return as_json(flag, await rules_for(db, flag.id))
