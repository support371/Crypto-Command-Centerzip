# CryptoSignal Trading Platform

## Architecture

Multi-service institutional trading platform with the following components:

### Services
| Service | Port | Status |
|---------|------|--------|
| Frontend (Next.js) | 5000 | Running (workflow) |
| Execution Core (FastAPI) | 8000 | Running (workflow) |
| Prediction Bot (FastAPI) | 8001 | Docker / manual |
| Guardian Bot (FastAPI) | 8002 | Docker / manual |

### Infrastructure (via Docker Compose)
- PostgreSQL + TimescaleDB — trading DB + time-series
- Redis — message broker between services

## Directory Structure

```
/
├── src/                        # Next.js frontend app (at root for Replit)
│   └── app/
│       ├── (pages)/            # dashboard, command-center, auth, settings, education, partners
│       ├── api/                # Next.js API routes (proxies to execution-core)
│       └── globals.css         # Tailwind v4 theme
├── execution-core/             # FastAPI execution engine
│   └── app/
│       ├── routers/            # account, positions, signals, orders, audit, guardian, price_feed
│       ├── models/             # paper_account, signal_store, audit_log
│       ├── adapters/           # base, btcc_adapter, bitget_adapter
│       └── middleware/         # Supabase JWT auth
├── prediction-bot/             # Signal generation service
│   └── app/
│       └── services/signal_generator.py
├── guardian-bot/               # Capital protection service
│   └── app/
│       └── services/guardian.py
├── infra/
│   └── migrations/             # PostgreSQL + TimescaleDB SQL migrations
├── docker-compose.yml          # Full stack orchestration
└── .env.example                # Environment template (copy to .env)
```

## Non-Negotiables (enforced in code)
- **Capital protection first**: Guardian bot has absolute override
- **No synthetic values in testnet/live**: Adapters enforce real data only
- **Guardian absolute override**: `close_all_positions()` cannot be blocked
- **All material actions auditable**: `audit()` called on every trade/signal/kill
- **No mainnet before testnet validation**: `btcc_testnet` and `bitget_testnet` default to `true`
- **All secrets in environment only**: `.env.example` documents all vars; no hardcoded secrets
- **Supabase JWT required on write routes**: `require_supabase_jwt` dependency on all POST routes

## Environment Variables

Copy `.env.example` to `.env` and fill in all values before running any service.

Key variables:
- `SUPABASE_JWT_SECRET` — required for JWT verification on write routes
- `BTCC_API_KEY`, `BTCC_API_SECRET` — BTCC exchange (testnet by default)
- `BITGET_API_KEY`, `BITGET_API_SECRET`, `BITGET_PASSPHRASE` — Bitget exchange
- `DATABASE_URL` — PostgreSQL + TimescaleDB connection string
- `REDIS_URL` — Redis connection string
- `KILL_SWITCH_SECRET` — required to reset kill-switch after trigger

## Kill-Switch

- **Auto-trigger**: Guardian bot monitors every 5s; triggers on:
  - Daily loss > `AUTO_KILL_LOSS_USD` (default: $1,000)
  - Drawdown > `AUTO_KILL_DRAWDOWN_PCT` (default: 5%)
  - Open positions > `MAX_OPEN_POSITIONS` (default: 10)
- **Manual trigger**: UI button in Command Center (requires Supabase JWT)
- **API trigger**: `POST /guardian/kill` (requires JWT)
- **Reset**: `POST /guardian/reset?secret=<KILL_SWITCH_SECRET>`

## Development Runbook

1. `cp .env.example .env` and fill in values
2. Start infrastructure: `docker-compose up postgres redis -d`
3. Apply migrations: `psql $DATABASE_URL < infra/migrations/001_init_schema.sql`
4. Frontend: runs automatically via workflow (port 5000)
5. Execution Core: runs automatically via workflow (port 8000)
6. Prediction Bot: `cd prediction-bot && uvicorn app.main:app --port 8001`
7. Guardian Bot: `cd guardian-bot && uvicorn app.main:app --port 8002`

## Testnet Validation Checklist

- [ ] BTCC testnet orders placed and confirmed
- [ ] Bitget testnet orders placed and confirmed
- [ ] Kill-switch tested (manual + auto-trigger)
- [ ] Reconciliation verified (positions match exchange)
- [ ] Guardian override tested under simulated breach
- [ ] Audit log verified for all material actions
- [ ] PostgreSQL + TimescaleDB migration applied
- [ ] Redis signal pipeline verified end-to-end
- [ ] Supabase JWT verified on all write routes

**No mainnet before all checklist items pass.**

## Remaining Work

See issue tracker for remaining items:
1. CCXT Pro live price feed connection
2. Redis pub/sub live wiring
3. PostgreSQL + TimescaleDB live persistence
4. Supabase JWT verification in production
5. Testnet validation pass
6. Production deployment runbook
