import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.asset import Asset
from app.schemas.asset import UploadUrlRequest, UploadUrlResponse, AssetCreate, AssetResponse, AssetReorderRequest
from app.services.s3 import generate_presigned_upload_url, get_public_url
from app.config import settings

router = APIRouter()


async def _get_project_or_404(project_id: uuid.UUID, user: User, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.organization_id == user.organization_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/assets/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    project_id: uuid.UUID,
    body: UploadUrlRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project_or_404(project_id, user, db)
    ext = body.filename.rsplit(".", 1)[-1].lower() if "." in body.filename else "bin"
    s3_key = f"uploads/{user.organization_id}/{project_id}/{uuid.uuid4()}.{ext}"
    upload_url = generate_presigned_upload_url(settings.s3_uploads_bucket, s3_key, body.mime_type)
    return UploadUrlResponse(upload_url=upload_url, s3_key=s3_key, s3_bucket=settings.s3_uploads_bucket)


@router.post("/{project_id}/assets", response_model=AssetResponse, status_code=201)
async def register_asset(
    project_id: uuid.UUID,
    body: AssetCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project_or_404(project_id, user, db)
    asset = Asset(id=uuid.uuid4(), project_id=project_id, **body.model_dump())
    db.add(asset)
    await db.flush()
    response = AssetResponse.model_validate(asset)
    response.url = get_public_url(asset.s3_bucket, asset.s3_key)
    return response


@router.get("/{project_id}/assets", response_model=list[AssetResponse])
async def list_assets(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project_or_404(project_id, user, db)
    result = await db.execute(
        select(Asset).where(Asset.project_id == project_id).order_by(Asset.sort_order, Asset.created_at)
    )
    assets = result.scalars().all()
    items = []
    for a in assets:
        r = AssetResponse.model_validate(a)
        r.url = get_public_url(a.s3_bucket, a.s3_key)
        items.append(r)
    return items


@router.delete("/{project_id}/assets/{asset_id}", status_code=204)
async def delete_asset(
    project_id: uuid.UUID,
    asset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project_or_404(project_id, user, db)
    result = await db.execute(select(Asset).where(Asset.id == asset_id, Asset.project_id == project_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await db.delete(asset)


@router.patch("/{project_id}/assets/reorder", status_code=200)
async def reorder_assets(
    project_id: uuid.UUID,
    body: AssetReorderRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project_or_404(project_id, user, db)
    for idx, asset_id in enumerate(body.asset_ids):
        result = await db.execute(select(Asset).where(Asset.id == asset_id, Asset.project_id == project_id))
        asset = result.scalar_one_or_none()
        if asset:
            asset.sort_order = idx
    return {"ok": True}
