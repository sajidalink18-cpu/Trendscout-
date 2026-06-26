import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Post
from .openai_service import embed_batch

logger = logging.getLogger(__name__)

async def embed_new_posts(db: AsyncSession) -> int:
    result = await db.execute(
        select(Post).where(Post.embedding.is_(None)).order_by(Post.fetched_at.desc())
    )
    posts: list[Post] = result.scalars().all()

    if not posts:
        return 0

    texts = [f"{p.title}\n\n{p.body or ''}" for p in posts]
    embeddings = await embed_batch(texts)

    for post, emb in zip(posts, embeddings):
        post.embedding = emb

    await db.commit()
    return len(posts)
