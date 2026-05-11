-- Wind Motion - Initial Database Schema
-- PostgreSQL Migration 001

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ── Whale Addresses ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS whales (
    address         VARCHAR(42) PRIMARY KEY,
    chain           VARCHAR(20) NOT NULL DEFAULT 'bsc',
    total_profit_usd    DOUBLE PRECISION DEFAULT 0,
    realized_pnl        DOUBLE PRECISION DEFAULT 0,
    win_rate            DOUBLE PRECISION DEFAULT 0,
    roi                 DOUBLE PRECISION DEFAULT 0,
    trade_count         INTEGER DEFAULT 0,
    token_count         INTEGER DEFAULT 0,
    last_active         TIMESTAMPTZ,
    labels              JSONB DEFAULT '[]',
    score               DOUBLE PRECISION DEFAULT 0,
    strategy_patterns   JSONB DEFAULT '[]',
    first_seen          TIMESTAMPTZ DEFAULT NOW(),
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_whales_chain ON whales(chain);
CREATE INDEX IF NOT EXISTS idx_whales_score ON whales(score DESC);
CREATE INDEX IF NOT EXISTS idx_whales_last_active ON whales(last_active DESC);
CREATE INDEX IF NOT EXISTS idx_whales_labels ON whales USING GIN(labels);

-- ── Transactions ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id              BIGSERIAL PRIMARY KEY,
    hash            VARCHAR(66) NOT NULL,
    from_address    VARCHAR(42) NOT NULL,
    to_address      VARCHAR(42) NOT NULL,
    chain           VARCHAR(20) NOT NULL DEFAULT 'bsc',
    block_number    BIGINT DEFAULT 0,
    timestamp       TIMESTAMPTZ,
    value_usd       DOUBLE PRECISION DEFAULT 0,
    token_address   VARCHAR(42),
    token_symbol    VARCHAR(20),
    token_amount    DOUBLE PRECISION DEFAULT 0,
    tx_type         VARCHAR(20) DEFAULT 'TRANSFER',
    dex             VARCHAR(50),
    gas_used        BIGINT DEFAULT 0,
    gas_price       BIGINT DEFAULT 0,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(hash, from_address)
);

CREATE INDEX IF NOT EXISTS idx_tx_from ON transactions(from_address);
CREATE INDEX IF NOT EXISTS idx_tx_to ON transactions(to_address);
CREATE INDEX IF NOT EXISTS idx_tx_token ON transactions(token_address);
CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_tx_type ON transactions(tx_type);
CREATE INDEX IF NOT EXISTS idx_tx_hash ON transactions(hash);

-- ── Filter Configurations ──────────────────────────────────
CREATE TABLE IF NOT EXISTS filters (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    chain           VARCHAR(20) DEFAULT 'bsc',
    config          JSONB NOT NULL DEFAULT '{}',
    auto_analyze    BOOLEAN DEFAULT FALSE,
    analyze_mode    VARCHAR(20) DEFAULT 'manual',
    analyze_frequency_hours INTEGER DEFAULT 6,
    analyze_depth   VARCHAR(20) DEFAULT 'standard',
    concurrent_limit INTEGER DEFAULT 3,
    cache_days      INTEGER DEFAULT 7,
    notify_on_complete BOOLEAN DEFAULT FALSE,
    notify_on_high_score BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Analysis Tasks ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analyses (
    id              VARCHAR(16) PRIMARY KEY,
    whale_address   VARCHAR(42) NOT NULL,
    analysis_type   VARCHAR(20) NOT NULL,  -- forward / reverse
    status          VARCHAR(20) DEFAULT 'pending',
    mode            VARCHAR(20) DEFAULT 'deep',
    chain           VARCHAR(20) DEFAULT 'bsc',
    progress_pct    DOUBLE PRECISION DEFAULT 0,
    current_phase   VARCHAR(50) DEFAULT '',
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    duration_s      DOUBLE PRECISION DEFAULT 0,
    report          JSONB,
    graph_data      JSONB,
    probability_timeline JSONB DEFAULT '[]',
    deliberation_records JSONB DEFAULT '[]',
    factor_scores   JSONB,
    matched_patterns JSONB DEFAULT '[]',
    error           TEXT,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyses_whale ON analyses(whale_address);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at DESC);

-- ── Rounds (Trading Rounds) ────────────────────────────────
CREATE TABLE IF NOT EXISTS rounds (
    id              VARCHAR(32) PRIMARY KEY,
    analysis_id     VARCHAR(16) REFERENCES analyses(id) ON DELETE CASCADE,
    whale_address   VARCHAR(42) NOT NULL,
    token_address   VARCHAR(42) NOT NULL,
    token_symbol    VARCHAR(20),
    start_time      TIMESTAMPTZ,
    end_time        TIMESTAMPTZ,
    total_invested_usd DOUBLE PRECISION DEFAULT 0,
    total_returned_usd DOUBLE PRECISION DEFAULT 0,
    net_profit_usd  DOUBLE PRECISION DEFAULT 0,
    roi             DOUBLE PRECISION DEFAULT 0,
    max_drawdown_pct DOUBLE PRECISION DEFAULT 0,
    avg_entry_price DOUBLE PRECISION DEFAULT 0,
    avg_exit_price  DOUBLE PRECISION DEFAULT 0,
    trade_count     INTEGER DEFAULT 0,
    hold_days       INTEGER DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'completed',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rounds_analysis ON rounds(analysis_id);
CREATE INDEX IF NOT EXISTS idx_rounds_whale ON rounds(whale_address);
CREATE INDEX IF NOT EXISTS idx_rounds_token ON rounds(token_address);

-- ── Decision Nodes ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS decision_nodes (
    id              VARCHAR(32) PRIMARY KEY,
    round_id        VARCHAR(32) REFERENCES rounds(id) ON DELETE CASCADE,
    node_type       VARCHAR(30) NOT NULL,
    timestamp       TIMESTAMPTZ,
    token_address   VARCHAR(42),
    token_symbol    VARCHAR(20),
    price_at_decision DOUBLE PRECISION DEFAULT 0,
    price_change_pct DOUBLE PRECISION DEFAULT 0,
    market_cap      DOUBLE PRECISION DEFAULT 0,
    liquidity_depth DOUBLE PRECISION DEFAULT 0,
    holder_count    INTEGER DEFAULT 0,
    volume_24h      DOUBLE PRECISION DEFAULT 0,
    social_mentions INTEGER DEFAULT 0,
    btc_trend       VARCHAR(20),
    market_sentiment VARCHAR(20),
    position_size_pct DOUBLE PRECISION DEFAULT 0,
    inferred_logic  TEXT,
    factor_scores   JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_decisions_round ON decision_nodes(round_id);
CREATE INDEX IF NOT EXISTS idx_decisions_type ON decision_nodes(node_type);

-- ── Factor Scores ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS factor_scores (
    id              SERIAL PRIMARY KEY,
    analysis_id     VARCHAR(16) REFERENCES analyses(id) ON DELETE CASCADE,
    factor_id       VARCHAR(5) NOT NULL,  -- F1-F5
    score           DOUBLE PRECISION DEFAULT 0,
    sub_scores      JSONB DEFAULT '{}',
    summary         TEXT DEFAULT '',
    evidence        JSONB DEFAULT '[]',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(analysis_id, factor_id)
);

CREATE INDEX IF NOT EXISTS idx_factors_analysis ON factor_scores(analysis_id);

-- ── Strategy Patterns ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS strategy_matches (
    id              SERIAL PRIMARY KEY,
    analysis_id     VARCHAR(16) REFERENCES analyses(id) ON DELETE CASCADE,
    whale_address   VARCHAR(42) NOT NULL,
    pattern_id      VARCHAR(50) NOT NULL,
    confidence      DOUBLE PRECISION DEFAULT 0,
    evidence        JSONB DEFAULT '[]',
    avg_roi         DOUBLE PRECISION DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patterns_analysis ON strategy_matches(analysis_id);
CREATE INDEX IF NOT EXISTS idx_patterns_whale ON strategy_matches(whale_address);
CREATE INDEX IF NOT EXISTS idx_patterns_pattern ON strategy_matches(pattern_id);

-- ── Whale Library (curated list) ───────────────────────────
CREATE TABLE IF NOT EXISTS whale_library (
    id              SERIAL PRIMARY KEY,
    address         VARCHAR(42) NOT NULL,
    chain           VARCHAR(20) DEFAULT 'bsc',
    nickname        VARCHAR(100),
    notes           TEXT,
    tags            JSONB DEFAULT '[]',
    added_at        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(address, chain)
);

-- ── Smart Recommendations ──────────────────────────────────
CREATE TABLE IF NOT EXISTS recommendations (
    id              SERIAL PRIMARY KEY,
    recommendation_type VARCHAR(50) NOT NULL,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    reason          TEXT,
    expected_impact TEXT,
    config_patch    JSONB,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending / applied / ignored
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Settings ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS settings (
    key             VARCHAR(100) PRIMARY KEY,
    value           JSONB NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default settings
INSERT INTO settings (key, value) VALUES
    ('api_keys', '{"bscscan": "", "deepseek": "", "qwen": ""}'),
    ('notifications', '{"email": false, "telegram": false, "webhook": ""}'),
    ('model_routing', '{"heavy": "deepseek-r1", "medium": "deepseek-v3", "light": "qwen-turbo"}'),
    ('cost_limits', '{"daily_yuan": 100, "single_yuan": 10}'),
    ('language', '"zh-CN"')
ON CONFLICT (key) DO NOTHING;
