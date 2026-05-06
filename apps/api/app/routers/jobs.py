import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.job import GenerationJob, JobStatus
from app.schemas.job import JobResponse, JobListResponse

router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GenerationJob)
        .join(Project, GenerationJob.project_id == Project.id)
        .where(GenerationJob.id == job_id, Project.organization_id == user.organization_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GenerationJob)
        .join(Project, GenerationJob.project_id == Project.id)
        .where(GenerationJob.id == job_id, Project.organization_id == user.organization_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in (JobStatus.QUEUED, JobStatus.RUNNING):
        raise HTTPException(status_code=400, detail="Job cannot be canceled in its current state")
    job.status = JobStatus.CANCELED
    if job.celery_task_id:
        from app.worker.celery_app import celery_app
        celery_app.control.revoke(job.celery_task_id, terminate=True)
    return job
