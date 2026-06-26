CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS posts (
    id          SERIAL PRIMARY KEY,
    reddit_id   VARCHAR(20) UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    body        TEXT,
    url         TEXT NOT NULL,
    subreddit   VARCHAR(100) NOT NULL,
    upvotes     INTEGER DEFAULT 0,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    fetched_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    embedding   vector(1536)
);

CREATE TABLE IF NOT EXISTS clusters (
    id              SERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    summary         TEXT,
    who_has_problem TEXT,
    why_it_matters  TEXT,
    saas_idea       TEXT,
    score           FLOAT DEFAULT 0,
    mention_count   INTEGER DEFAULT 0,
    avg_upvotes     FLOAT DEFAULT 0,
    growth_rate     FLOAT DEFAULT 0,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cluster_posts (
    cluster_id  INTEGER REFERENCES clusters(id) ON DELETE CASCADE,
    post_id     INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    PRIMARY KEY (cluster_id, post_id)
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id          SERIAL PRIMARY KEY,
    started_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    status      VARCHAR(20) DEFAULT 'running',
    message     TEXT,
    posts_fetched   INTEGER DEFAULT 0,
    clusters_found  INTEGER DEFAULT 0
);
