"""
Master pipeline task. Orchestrates all steps and publishes real-time
progress to Redis pub/sub (consumed by WebSocket clients).
"""
import json
import os
import shutil
import uuid
from datetime import datetime, timezone

import redis
from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models.job import GenerationJob, JobStatus, JobStep
from app.models.project import Project, ProjectStatus
from app.models.asset import Asset
from app.models.subscription import Subscription
from app.models.video import Video
from app.worker.celery_app import celery_app
from app.worker.tasks.script_gen import generate_script
from app.worker.tasks.voiceover import generate_voiceover
from app.worker.tasks.music_fetch import fetch_music
from app.worker.tasks.compositor import compose_video
from app.worker.utils.store_specs import get_primary_spec
from app.worker.utils.ffmpeg_helpers import validate_output
from app.worker.utils.watermark import add_watermark
from app.services.s3 import upload_file_local, download_file_local

# Sync engine for Celery workers (Celery doesn't play well with asyncio)
_sync_engine = create_engine(
    settings.database_url.replace("+asyncpg", ""),
    pool_pre_ping=True,
)
SyncSession = sessionmaker(_sync_engine)

_redis = redis.from_url(settings.redis_url, decode_responses=True)


def _publish(job_id: str, payload: dict) -> None:
    _redis.publish(f"job:{job_id}", json.dumps(payload))


def _update_job(session: Session, job: GenerationJob, **kwargs) -> None:
    for k, v in kwargs.items():
        setattr(job, k, v)
    session.commit()
    _publish(str(job.id), {
        "type": "progress",
        "job_id": str(job.id),
        "step": job.current_step,
        "progress_pct": job.progress_pct,
        "status": job.status,
    })


class PipelineTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        job_id = args[0] if args else None
        if not job_id:
            return
        with SyncSession() as session:
            job = session.get(GenerationJob, uuid.UUID(job_id))
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(exc)
                session.commit()
                proj = session.get(Project, job.project_id)
                if proj:
                    proj.status = ProjectStatus.FAILED
                    session.commit()
        _publish(job_id, {"type": "failed", "job_id": job_id, "error": str(exc)})


@celery_app.task(bind=True, base=PipelineTask, name="app.worker.tasks.orchestrator.generate_video_task", max_retries=2)
def generate_video_task(self, job_id: str) -> dict:
    workdir = f"/tmp/aivid/{job_id}"
    os.makedirs(workdir, exist_ok=True)

    with SyncSession() as session:
        job = session.get(GenerationJob, uuid.UUID(job_id))
        if not job:
            raise ValueError(f"Job {job_id} not found")

        project = session.get(Project, job.project_id)
        if not project:
            raise ValueError(f"Project {job.project_id} not found")

        # ── Step 0: Pre-flight ──────────────────────────────────────────────
        _update_job(session, job, status=JobStatus.RUNNING, current_step=JobStep.PREFLIGHT,
                    progress_pct=5, started_at=datetime.now(timezone.utc))

        sub = session.query(Subscription).filter_by(organization_id=project.organization_id).first()
        is_free_tier = (not sub) or (sub.tier == "free")

        screenshots = session.query(Asset).filter(
            Asset.project_id == project.id,
            Asset.asset_type.in_(["screenshot_iphone", "screenshot_ipad", "screenshot_android"]),
        ).order_by(Asset.sort_order).all()

        icon_asset = session.query(Asset).filter(
            Asset.project_id == project.id, Asset.asset_type == "icon"
        ).first()

        if not screenshots:
            raise ValueError("At least one screenshot is required")

        spec = get_primary_spec(project.target_store)

        # ── Step 1: Download assets from S3 ────────────────────────────────
        _update_job(session, job, current_step=JobStep.ASSET_PREP, progress_pct=15)

        ss_paths: list[str] = []
        for idx, ss in enumerate(screenshots[:6]):
            local_path = os.path.join(workdir, f"screenshot_{idx}{os.path.splitext(ss.filename)[1]}")
            download_file_local(ss.s3_bucket, ss.s3_key, local_path)
            ss_paths.append(local_path)

        icon_path: str | None = None
        if icon_asset:
            icon_path = os.path.join(workdir, f"icon{os.path.splitext(icon_asset.filename)[1]}")
            download_file_local(icon_asset.s3_bucket, icon_asset.s3_key, icon_path)

        _update_job(session, job, current_step=JobStep.ASSET_PREP, progress_pct=30)

        # ── Step 2: Script Generation ───────────────────────────────────────
        _update_job(session, job, current_step=JobStep.SCRIPT_GEN, progress_pct=35)

        script = generate_script(
            app_name=project.app_name,
            description=project.app_description or "",
            category=project.app_category or "App",
            keywords=project.keywords or [],
            style_theme=project.style_theme,
            target_store=project.target_store,
            num_screenshots=len(ss_paths),
        )
        _update_job(session, job, progress_pct=45)

        # ── Step 3: Voiceover ───────────────────────────────────────────────
        _update_job(session, job, current_step=JobStep.VOICEOVER, progress_pct=50)

        voice_path = os.path.join(workdir, "voiceover.wav")
        generate_voiceover(script["narration_text"], project.style_theme, voice_path)
        _update_job(session, job, progress_pct=60)

        # ── Step 4: Background Music ────────────────────────────────────────
        _update_job(session, job, current_step=JobStep.MUSIC_FETCH, progress_pct=62)

        music_path = os.path.join(workdir, "music.mp3")
        fetch_music(project.style_theme, 28.0, music_path)
        _update_job(session, job, progress_pct=68)

        # ── Step 5: Video Composition ───────────────────────────────────────
        _update_job(session, job, current_step=JobStep.COMPOSITION, progress_pct=70)

        raw_output = os.path.join(workdir, "output_raw.mp4")
        compose_video(
            workdir=workdir,
            screenshot_paths=ss_paths,
            icon_path=icon_path,
            voiceover_path=voice_path,
            music_path=music_path,
            script=script,
            spec=spec,
            style_theme=project.style_theme,
            app_name=project.app_name,
            output_path=raw_output,
        )
        _update_job(session, job, progress_pct=88)

        # ── Step 6: Watermark (free tier) ──────────────────────────────────
        final_output = os.path.join(workdir, "output_final.mp4")
        if is_free_tier:
            add_watermark(raw_output, final_output)
        else:
            os.rename(raw_output, final_output)

        # ── Step 7: Quality Check ───────────────────────────────────────────
        _update_job(session, job, current_step=JobStep.QUALITY_CHECK, progress_pct=90)

        errors = validate_output(final_output, spec)
        if errors:
            raise ValueError(f"Quality check failed: {'; '.join(errors)}")

        # ── Step 8: Upload to S3 ────────────────────────────────────────────
        _update_job(session, job, current_step=JobStep.FINALIZE, progress_pct=93)

        output_key = f"outputs/{project.organization_id}/{project.id}/{job_id}.mp4"
        upload_file_local(final_output, settings.s3_outputs_bucket, output_key, "video/mp4")

        file_size = os.path.getsize(final_output)
        cdn_url = f"{settings.s3_public_url}/{settings.s3_outputs_bucket}/{output_key}" if settings.s3_public_url else None

        # ── Step 9: Save video record ───────────────────────────────────────
        import subprocess, json as _json
        probe_result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", final_output],
            capture_output=True, text=True,
        )
        duration_seconds = float(_json.loads(probe_result.stdout)["format"]["duration"])

        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(days=30) if is_free_tier else None

        video = Video(
            id=uuid.uuid4(),
            project_id=project.id,
            job_id=job.id,
            target_store=project.target_store,
            orientation=spec.orientation,
            resolution=f"{spec.width}x{spec.height}",
            duration_seconds=duration_seconds,
            file_size_bytes=file_size,
            s3_key=output_key,
            s3_bucket=settings.s3_outputs_bucket,
            cdn_url=cdn_url,
            watermarked=is_free_tier,
            generated_script=json.dumps(script),
            expires_at=expires_at,
        )
        session.add(video)

        # Update project and job
        project.status = ProjectStatus.COMPLETED
        job.status = JobStatus.COMPLETED
        job.progress_pct = 100
        job.completed_at = datetime.now(timezone.utc)

        # Increment usage counter
        if sub:
            sub.videos_used_this_period += 1

        session.commit()

    # Cleanup
    shutil.rmtree(workdir, ignore_errors=True)

    _publish(job_id, {
        "type": "completed",
        "job_id": job_id,
        "video_id": str(video.id),
        "cdn_url": cdn_url,
    })

    return {"job_id": job_id, "video_id": str(video.id)}
