from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Flag, Project, Rule
from app.services.bucketing import in_rollout
from app.services.rules import all_rules_match

router = APIRouter()


class EvaluateIn(BaseModel):
    user_key: str
    attributes: dict = {}


@router.post("/{project_key}/evaluate")
async def evaluate(
    project_key: str, body: EvaluateIn, db: AsyncSession = Depends(get_db)
):
    """Every flag in the project, decided for one user."""
    project = await db.scalar(select(Project).where(Project.key == project_key))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(select(Flag).where(Flag.project_id == project.id))
    flags = list(result.scalars().all())

    rules_result = await db.execute(
        select(Rule).where(Rule.flag_id.in_([flag.id for flag in flags]))
    )
    rules_by_flag: dict[int, list[Rule]] = {}
    for rule in rules_result.scalars().all():
        rules_by_flag.setdefault(rule.flag_id, []).append(rule)

    decided = {}
    for flag in flags:
        decided[flag.key] = decide(flag, rules_by_flag.get(flag.id, []), body)

    return {"user_key": body.user_key, "flags": decided}


def decide(flag: Flag, rules: list[Rule], body: EvaluateIn) -> bool:
    if not flag.enabled:
        return False
    if not all_rules_match(rules, body.attributes):
        return False
    return in_rollout(flag.key, body.user_key, flag.rollout_percent)
