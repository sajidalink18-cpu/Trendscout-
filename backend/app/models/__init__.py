from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Text, Float, DateTime, ForeignKey,
    func, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reddit_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    subreddit: Mapped[str] = mapped_column(String(100), nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))

    cluster_posts: Mapped[List["ClusterPost"]] = relationship(back_populates="post")


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    who_has_problem: Mapped[Optional[str]] = mapped_column(Text)
    why_it_matters: Mapped[Optional[str]] = mapped_column(Text)
    saas_idea: Mapped[Optional[str]] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    mention_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_upvotes: Mapped[float] = mapped_column(Float, default=0.0)
    growth_rate: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    cluster_posts: Mapped[List["ClusterPost"]] = relationship(
        back_populates="cluster", cascade="all, delete-orphan"
    )


class ClusterPost(Base):
    __tablename__ = "cluster_posts"
    __table_args__ = (UniqueConstraint("cluster_id", "post_id"),)

    cluster_id: Mapped[int] = mapped_column(ForeignKey("clusters.id", ondelete="CASCADE"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)

    cluster: Mapped["Cluster"] = relationship(back_populates="cluster_posts")
    post: Mapped["Post"] = relationship(back_populates="cluster_posts")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="running")
    message: Mapped[Optional[str]] = mapped_column(Text)
    posts_fetched: Mapped[int] = mapped_column(Integer, default=0)
    clusters_found: Mapped[int] = mapped_column(Integer, default=0)
