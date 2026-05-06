import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.job import GenerationJob, JobStatus
from app.models.subscription import Subscription
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.schemas.job import JobResponse

router = APIRouter()


async def _get_project_or_404(project_id: uuid.UUID, user: User, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.organization_id == user.organization_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = Project(
        id=uuid.uuid4(),
        organization_id=user.organization_id,
        created_by=user.id,
        **body.model_dump(),
    )
    db.add(project)
    await db.flush()
    return project


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    count_result = await db.execute(
        select(func.count()).select_from(Project).where(Project.organization_id == user.organization_id)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(Project)
        .where(Project.organization_id == user.organization_id)
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    projects = result.scalars().all()
    return ProjectListResponse(items=list(projects), total=total, page=page, page_size=page_size)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_project_or_404(project_id, user, db)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_or_404(project_id, user, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_or_404(project_id, user, db)
    await db.delete(project)


@router.post("/{project_id}/generate", response_model=JobResponse, status_code=202)
async def generate_video(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_or_404(project_id, user, db)

    # Check subscription quota
    sub_result = await db.execute(
        select(Subscription).where(Subscription.organization_id == user.organization_id)
    )
    subscription = sub_result.scalar_one_or_none()
    if not subscription or not subscription.has_quota or not subscription.is_active:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Video quota exceeded. Please upgrade your plan.",
        )

    # Cancel any running jobs for this project
    running_result = await db.execute(
        select(GenerationJob).where(
            GenerationJob.project_id == project_id,
            GenerationJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]),
        )
    )
    for job in running_result.scalars().all():
        job.status = JobStatus.CANCELED

    job = GenerationJob(id=uuid.uuid4(), project_id=project_id, status=JobStatus.QUEUED)
    db.add(job)
    project.status = ProjectStatus.GENERATING
    await db.flush()

    # Dispatch Celery task
    from app.worker.tasks.orchestrator import generate_video_task
    task = generate_video_task.delay(str(job.id))
    job.celery_task_id = task.id

    return job
