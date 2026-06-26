import logging
from datetime import datetime, timedelta, timezone
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import get_settings
from ..models import Post, Cluster, ClusterPost
from .openai_service import generate_cluster_summary

logger = logging.getLogger(__name__)
settings = get_settings()


def _greedy_cluster(embeddings, threshold):
    n = len(embeddings)
    assigned = [False] * n
    clusters = []
    sims = cosine_similarity(embeddings)
    for i in range(n):
        if assigned[i]:
            continue
        cluster = [i]
        assigned[i] = True
        for j in range(i + 1, n):
            if not assigned[j] and sims[i][j] >= threshold:
                cluster.append(j)
                assigned[j] = True
        clusters.append(cluster)
    return clusters


def _compute_score(mention_count, growth_rate, avg_upvotes):
    return (mention_count * 2) + (growth_rate * 3) + (avg_upvotes * 0.5)


def _compute_growth(posts):
    now = datetime.now(tz=timezone.utc)
    cutoff_recent = now - timedelta(days=7)
    cutoff_prev = now - timedelta(days=14)
    recent = sum(1 for p in posts if p.created_at >= cutoff_recent)
    previous = sum(1 for p in posts if cutoff_prev <= p.created_at < cutoff_recent)
    if previous == 0:
        return float(recent)
    return round((recent - previous) / previous * 100, 2)


async def run_clustering(db: AsyncSession) -> int:
    result = await db.execute(
        select(Post).where(Post.embedding.is_not(None)).order_by(Post.created_at.desc())
    )
    posts = result.scalars().all()

    if len(posts) < 2:
        return 0

    embeddings = np.array([p.embedding for p in posts], dtype=np.float32)
    raw_clusters = _greedy_cluster(embeddings, threshold=settings.cluster_threshold)
    meaningful = [c for c in raw_clusters if len(c) >= 2]

    await db.execute(delete(Cluster))
    await db.commit()

    created = 0
    for idx_list in meaningful:
        cluster_posts_objs = [posts[i] for i in idx_list]
        avg_upvotes = sum(p.upvotes for p in cluster_posts_objs) / len(cluster_posts_objs)
        growth_rate = _compute_growth(cluster_posts_objs)
        mention_count = len(cluster_posts_objs)
        score = _compute_score(mention_count, growth_rate, avg_upvotes)

        sample = [{"title": p.title, "body": p.body} for p in cluster_posts_objs[:8]]
        try:
            summary_data = await generate_cluster_summary(sample)
        except Exception:
            summary_data = {"title": cluster_posts_objs[0].title[:60], "summary": "", "who_has_problem": "", "why_it_matters": "", "saas_idea": ""}

        cluster = Cluster(
            title=summary_data.get("title", "Untitled")[:200],
            summary=summary_data.get("summary", ""),
            who_has_problem=summary_data.get("who_has_problem", ""),
            why_it_matters=summary_data.get("why_it_matters", ""),
            saas_idea=summary_data.get("saas_idea", ""),
            score=score,
            mention_count=mention_count,
            avg_upvotes=avg_upvotes,
            growth_rate=growth_rate,
        )
        db.add(cluster)
        await db.flush()

        for post in cluster_posts_objs:
            db.add(ClusterPost(cluster_id=cluster.id, post_id=post.id))

        created += 1

    await db.commit()
    return created
