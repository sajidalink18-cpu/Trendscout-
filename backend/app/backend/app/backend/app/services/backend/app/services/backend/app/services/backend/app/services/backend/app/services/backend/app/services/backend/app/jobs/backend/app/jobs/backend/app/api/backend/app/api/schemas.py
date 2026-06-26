from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PostSchema(BaseModel):
    id: int
    reddit_id: str
    title: str
    body: Optional[str]
    url: str
    subreddit: str
    upvotes: int
    created_at: datetime

    class Config:
        from_attributes = True


class OpportunitySchema(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    who_has_problem: Optional[str]
    why_it_matters: Optional[str]
    saas_idea: Optional[str]
    score: float
    mention_count: int
    avg_upvotes: float
    growth_rate: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OpportunityDetailSchema(OpportunitySchema):
    posts: list[PostSchema] = []


class TriggerResponseSchema(BaseModel):
    message: str
    run_id: Optional[int] = None
