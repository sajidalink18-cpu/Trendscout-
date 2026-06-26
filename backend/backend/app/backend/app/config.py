from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://trendscout:trendscout_pass@postgres:5432/trendscout"
    openai_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "TrendScoutAI/1.0"
    posts_per_subreddit: int = 100
    cluster_threshold: float = 0.82
    top_opportunities: int = 20
    target_subreddits: list[str] = [
        "entrepreneur",
        "startups",
        "smallbusiness",
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
