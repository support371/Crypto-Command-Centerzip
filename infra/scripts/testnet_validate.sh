#!/usr/bin/env bash
# Testnet Validation Script
# Runs all pre-live checks. Must pass 100% before any mainnet usage.

set -euo pipefail

CORE="http://localhost:8000"
BOT_PRED="http://localhost:8001"
BOT_GUARD="http://localhost:8002"
PASS=0
FAIL=0

check() {
  local name="$1"
  local condition="$2"
  if eval "$condition" > /dev/null 2>&1; then
    echo "  ✓ $name"
    ((PASS++))
  else
    echo "  ✗ FAIL: $name"
    ((FAIL++))
  fi
}

echo "========================================"
echo "  CryptoSignal Testnet Validation"
echo "========================================"

echo ""
echo "1. Service Health Checks"
check "Execution Core health" "curl -sf $CORE/health"
check "Prediction Bot health" "curl -sf $BOT_PRED/health"
check "Guardian Bot health" "curl -sf $BOT_GUARD/health"

echo ""
echo "2. API Endpoints"
check "Account summary" "curl -sf $CORE/account/summary | grep -q balance"
check "Positions list" "curl -sf $CORE/positions | grep -q positions"
check "Signals recent" "curl -sf $CORE/signals/recent | grep -q signals"
check "Guardian status" "curl -sf $BOT_GUARD/status | grep -q state"
check "Audit logs" "curl -sf $CORE/audit/logs | grep -q logs"

echo ""
echo "3. Kill-Switch"
echo "  (Manual verification required — trigger and verify all positions close)"
check "Kill endpoint exists" "curl -sf -o /dev/null -w '%{http_code}' -X POST $CORE/guardian/kill -H 'Content-Type: application/json' -d '{\"reason\":\"validation_test\"}' | grep -qE '200|401'"

echo ""
echo "4. Exchange Adapters (testnet mode)"
if [ -n "${BTCC_API_KEY:-}" ] && [ -n "${BTCC_API_SECRET:-}" ]; then
  check "BTCC testnet configured" "[ '${BTCC_TESTNET:-true}' = 'true' ]"
fi
if [ -n "${BITGET_API_KEY:-}" ] && [ -n "${BITGET_API_SECRET:-}" ]; then
  check "Bitget testnet configured" "[ '${BITGET_TESTNET:-true}' = 'true' ]"
fi

echo ""
echo "5. Environment Safety"
check "CCXT sandbox mode active" "[ '${CCXT_SANDBOX_MODE:-true}' = 'true' ]"
check "APP_ENV not production" "[ '${APP_ENV:-development}' != 'production' ]"
check "Supabase JWT secret set" "[ -n '${SUPABASE_JWT_SECRET:-}' ]"
check "Kill-switch secret set" "[ -n '${KILL_SWITCH_SECRET:-}' ]"

echo ""
echo "========================================"
echo "  RESULTS: $PASS passed, $FAIL failed"
echo "========================================"

if [ "$FAIL" -gt 0 ]; then
  echo "  STATUS: FAIL — Do NOT proceed to mainnet"
  exit 1
else
  echo "  STATUS: PASS — Safe to proceed with testnet trading"
  echo "  NOTE: Live exchange validation still required before mainnet"
fi
