#!/usr/bin/env bash
# Start all CryptoSignal services locally (without Docker)
# Usage: ./infra/scripts/start_services.sh [testnet|paper]

set -euo pipefail

ENV=${1:-paper}
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "================================================"
echo "  CryptoSignal Platform — Starting services"
echo "  Mode: $ENV"
echo "================================================"

# Validate environment
if [ ! -f "$ROOT/.env" ]; then
  echo "ERROR: .env file not found. Copy .env.example to .env and fill in values."
  exit 1
fi

export $(grep -v '^#' "$ROOT/.env" | xargs)

# Override APP_ENV with argument
export APP_ENV="$ENV"

if [ "$ENV" = "production" ]; then
  echo "CRITICAL: Production mode requires testnet validation to have passed."
  echo "All exchange testnet flags must be explicitly set to false."
  read -p "Type 'CONFIRMED' to proceed: " confirmation
  if [ "$confirmation" != "CONFIRMED" ]; then
    echo "Aborted."
    exit 1
  fi
fi

# Start infrastructure (requires Docker)
echo "Starting infrastructure (PostgreSQL + Redis)..."
docker-compose up postgres redis -d
sleep 3

# Apply migrations if needed
if [ -n "${DATABASE_URL:-}" ]; then
  echo "Applying database migrations..."
  psql "$DATABASE_URL" < "$ROOT/infra/migrations/001_init_schema.sql" || echo "Migration may already be applied"
fi

# Start execution core
echo "Starting Execution Core on port 8000..."
cd "$ROOT/execution-core"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
EXECUTION_PID=$!

# Start prediction bot
echo "Starting Prediction Bot on port 8001..."
cd "$ROOT/prediction-bot"
uvicorn app.main:app --host 0.0.0.0 --port 8001 &
PREDICTION_PID=$!

# Start guardian bot
echo "Starting Guardian Bot on port 8002..."
cd "$ROOT/guardian-bot"
uvicorn app.main:app --host 0.0.0.0 --port 8002 &
GUARDIAN_PID=$!

# Start frontend
echo "Starting Frontend on port 5000..."
cd "$ROOT"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================================"
echo "  All services started"
echo "  Frontend:       http://localhost:5000"
echo "  Execution Core: http://localhost:8000/docs"
echo "  Prediction Bot: http://localhost:8001/docs"
echo "  Guardian Bot:   http://localhost:8002/docs"
echo "================================================"
echo ""
echo "PIDs: execution=$EXECUTION_PID prediction=$PREDICTION_PID guardian=$GUARDIAN_PID frontend=$FRONTEND_PID"
echo "Stop all: kill $EXECUTION_PID $PREDICTION_PID $GUARDIAN_PID $FRONTEND_PID"

wait
