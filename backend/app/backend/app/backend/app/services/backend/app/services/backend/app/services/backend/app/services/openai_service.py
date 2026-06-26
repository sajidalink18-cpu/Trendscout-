import asyncio
import json
import logging
from typing import Optional

from openai import AsyncOpenAI
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: Optional[AsyncOpenAI] = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def embed_text(text: str) -> list[float]:
    client = get_client()
    resp = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000],
    )
    return resp.data[0].embedding


async def embed_batch(texts: list[str], batch_size: int = 50) -> list[list[float]]:
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        client = get_client()
        resp = await client.embeddings.create(
            model="text-embedding-3-small",
            input=[t[:8000] for t in batch],
        )
        results.extend([d.embedding for d in resp.data])
        await asyncio.sleep(0.2)
    return results


async def generate_cluster_summary(posts_sample: list[dict]) -> dict:
    post_texts = "\n\n".join(
        f"[{i+1}] {p['title']}\n{(p.get('body') or '')[:300]}"
        for i, p in enumerate(posts_sample[:8])
    )

    prompt = f"""You are analyzing Reddit complaints from entrepreneur communities.

Posts:
{post_texts}

Respond ONLY with valid JSON with these keys:
{{
  "title": "Short problem title (max 60 chars)",
  "summary": "2-3 sentence description",
  "who_has_problem": "1 sentence: who has this problem",
  "why_it_matters": "1-2 sentences: business impact",
  "saas_idea": "1-2 sentence SaaS idea to solve this"
}}"""

    client = get_client()
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.3,
    )

    try:
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {
            "title": "Untitled Opportunity",
            "summary": "",
            "who_has_problem": "",
            "why_it_matters": "",
            "saas_idea": "",
      }
