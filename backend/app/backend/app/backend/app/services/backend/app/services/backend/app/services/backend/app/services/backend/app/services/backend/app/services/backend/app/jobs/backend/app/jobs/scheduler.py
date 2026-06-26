import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import update
from ..database import AsyncSessionLocal
from ..models import AnalysisRun
from .services.reddit import collect_posts
from .services.embeddings import embed_new_posts
from .services.clustering import run_clustering

logger = logging.getLogger(__name__)


async def run_full_pipeline() -> dict:
    async with AsyncSessionLocal() as db:
        run = AnalysisRun(status="running")
        db.add(run)
        await db.commit()
        await db.refresh(run)
        run_id = run.id

    result = {"run_id": run_id, "posts_fetched": 0, "clusters_found": 0, "status": "success", "message": ""}

    try:
        async with AsyncSessionLocal() as db:
            result["posts_fetched"] = await collect_posts(db)
        async with AsyncSessionLocal() as db:
            await embed_new_posts(db)
        async with AsyncSessionLocal() as db:
            result["clusters_found"] = await run_clustering(db)
    except Exception as exc:
        result["status"] = "error"
        result["message"] = str(exc)

    async with AsyncSessionLocal() as db:
        await db.execute(
            update(AnalysisRun).where(AnalysisRun.id == run_id).values(
                finished_at=datetime.now(tz=timezone.utc),
                status=result["status"],
                message=result["message"],
                posts_fetched=result["posts_fetched"],
                clusters_found=result["clusters_found"],
            )
        )
        await db.commit()

    return result


_scheduler = None


def start_scheduler():
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(run_full_pipeline, "interval", hours=24, id="full_pipeline", replace_existing=True)
    _scheduler.start()


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
