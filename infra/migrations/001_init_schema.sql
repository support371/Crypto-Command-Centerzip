-- ============================================================
-- 001 — Initial Schema: PostgreSQL + TimescaleDB
-- Creates core trading tables and hypertables for time-series.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ── Audit Events ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level       VARCHAR(10) NOT NULL CHECK (level IN ('info', 'warn', 'error', 'success')),
    source      VARCHAR(100) NOT NULL,
    message     TEXT NOT NULL,
    metadata    JSONB DEFAULT '{}'
);

SELECT create_hypertable('audit_events', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_audit_events_source ON audit_events(source);
CREATE INDEX IF NOT EXISTS idx_audit_events_level ON audit_events(level);

-- ── Signals ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    symbol          VARCHAR(30) NOT NULL,
    direction       VARCHAR(10) NOT NULL CHECK (direction IN ('long', 'short')),
    strength        FLOAT NOT NULL CHECK (strength >= 0 AND strength <= 1),
    source          VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    metadata        JSONB DEFAULT '{}'
);

SELECT create_hypertable('signals', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);

-- ── Orders ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    exchange        VARCHAR(50) NOT NULL,
    exchange_order_id VARCHAR(200),
    symbol          VARCHAR(30) NOT NULL,
    side            VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell')),
    order_type      VARCHAR(20) NOT NULL,
    amount          NUMERIC(20, 8) NOT NULL,
    price           NUMERIC(20, 8),
    filled_price    NUMERIC(20, 8),
    status          VARCHAR(30) NOT NULL DEFAULT 'pending',
    signal_id       UUID REFERENCES signals(id),
    reason          TEXT,
    metadata        JSONB DEFAULT '{}'
);

SELECT create_hypertable('orders', 'created_at', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_exchange ON orders(exchange);

-- ── Positions ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS positions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opened_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMPTZ,
    exchange        VARCHAR(50) NOT NULL,
    symbol          VARCHAR(30) NOT NULL,
    side            VARCHAR(10) NOT NULL,
    size            NUMERIC(20, 8) NOT NULL,
    entry_price     NUMERIC(20, 8) NOT NULL,
    exit_price      NUMERIC(20, 8),
    realized_pnl    NUMERIC(20, 8),
    status          VARCHAR(20) NOT NULL DEFAULT 'open',
    metadata        JSONB DEFAULT '{}'
);

SELECT create_hypertable('positions', 'opened_at', if_not_exists => TRUE);

-- ── Equity History ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS equity_history (
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    balance     NUMERIC(20, 4) NOT NULL,
    equity      NUMERIC(20, 4) NOT NULL,
    unrealized_pnl NUMERIC(20, 4) NOT NULL DEFAULT 0,
    exchange    VARCHAR(50) NOT NULL DEFAULT 'aggregate'
);

SELECT create_hypertable('equity_history', 'timestamp', if_not_exists => TRUE);

-- ── Kill-Switch Events ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS kill_switch_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    triggered_by VARCHAR(50) NOT NULL,  -- 'guardian_auto' | 'manual_ui' | 'api'
    reason      TEXT NOT NULL,
    positions_closed INT DEFAULT 0,
    reset_at    TIMESTAMPTZ,
    reset_by    VARCHAR(100)
);
