from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.milestone import Milestone
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate

async def create_milestone(db: AsyncSession, milestone_in: MilestoneCreate) -> Milestone:
    db_milestone = Milestone(**milestone_in.model_dump())
    db.add(db_milestone)
    await db.commit()
    await db.refresh(db_milestone)
    return db_milestone

async def get_milestone(db: AsyncSession, milestone_id: int) -> Milestone:
    query = select(Milestone).where(Milestone.id == milestone_id)
    result = await db.execute(query)
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    return milestone

async def list_milestones(db: AsyncSession, project_id: int = None, skip: int = 0, limit: int = 100) -> list[Milestone]:
    query = select(Milestone)
    if project_id:
        query = query.where(Milestone.project_id == project_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())

async def update_milestone(db: AsyncSession, milestone_id: int, milestone_in: MilestoneUpdate) -> Milestone:
    milestone = await get_milestone(db, milestone_id)
    update_data = milestone_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(milestone, field, value)
    await db.commit()
    await db.refresh(milestone)
    return milestone

async def delete_milestone(db: AsyncSession, milestone_id: int):
    milestone = await get_milestone(db, milestone_id)
    await db.delete(milestone)
    await db.commit()
