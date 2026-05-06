import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.video import Video
from app.schemas.video import VideoResponse, VideoListResponse
from app.services.s3 import generate_presigned_download_url

router = APIRouter()


@router.get("/projects/{project_id}/videos", response_model=VideoListResponse)
async def list_videos(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    proj_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.organization_id == user.organization_id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Video).where(Video.project_id == project_id).order_by(Video.created_at.desc())
    )
    return VideoListResponse(items=list(result.scalars().all()))


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Video)
        .join(Project, Video.project_id == Project.id)
        .where(Video.id == video_id, Project.organization_id == user.organization_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.get("/videos/{video_id}/download")
async def download_video(
    video_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Video)
        .join(Project, Video.project_id == Project.id)
        .where(Video.id == video_id, Project.organization_id == user.organization_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    download_url = generate_presigned_download_url(video.s3_bucket, video.s3_key, expires_in=300)
    return RedirectResponse(url=download_url)
