import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import Cluster, ClusterPost, Post, AnalysisRun
from ..jobs.scheduler import run_full_pipeline
from .schemas import OpportunitySchema, OpportunityDetailSchema, PostSchema, TriggerResponseSchema
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter()


@router.get("/opportunities", response_model=list[OpportunitySchema])
async def get_opportunities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Cluster).order_by(desc(Cluster.score)).limit(settings.top_opportunities)
    )
    return result.scalars().all()


@router.get("/opportunity/{cluster_id}", response_model=OpportunityDetailSchema)
async def get_opportunity(cluster_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Cluster).where(Cluster.id == cluster_id)
        .options(selectinload(Cluster.cluster_posts).selectinload(ClusterPost.post))
    )
    cluster = result.scalar_one_or_none()
    if not cluster:
        raise HTTPException(status_code=404, detail="Not found")
    posts = [cp.post for cp in cluster.cluster_posts]
    detail = OpportunityDetailSchema.model_validate(cluster)
    detail.posts = [PostSchema.model_validate(p) for p in posts]
    return detail


@router.post("/run-analysis", response_model=TriggerResponseSchema)
async def trigger_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_full_pipeline)
    return TriggerResponseSchema(message="Analysis pipeline started in background.")


@router.get("/status")
async def get_status(db: AsyncSession = Depends(get_db)):
    post_count = (await db.execute(select(func.count()).select_from(Post))).scalar()
    cluster_count = (await db.execute(select(func.count()).select_from(Cluster))).scalar()
    embedded_count = (await db.execute(select(func.count()).select_from(Post).where(Post.embedding.is_not(None)))).scalar()
    last_run = (await db.execute(select(AnalysisRun).order_by(desc(AnalysisRun.started_at)).limit(1))).scalar_one_or_none()
    return {
        "posts_total": post_count,
        "posts_embedded": embedded_count,
        "clusters_total": cluster_count,
        "last_run": {
            "id": last_run.id,
            "status": last_run.status,
            "started_at": last_run.started_at,
            "finished_at": last_run.finished_at,
            "posts_fetched": last_run.posts_fetched,
            "clusters_found": last_run.clusters_found,
        } if last_run else None,
    }
