#!/usr/bin/env bash
# ============================================================
# KAUSHALYA — Development Startup Script
# ============================================================
# Starts MongoDB (if not running), FastAPI backend, and the
# Vite frontend dev server in three separate terminal panes.
#
# Usage:
#   chmod +x start.sh
#   ./start.sh
#
# Prerequisites:
#   - MongoDB extracted to ~/mongodb  (see README for install)
#   - Python venv created at backend/venv  (pip install -r requirements.txt)
#   - pnpm installed and dependencies installed  (pnpm install)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PNPM_BIN="$HOME/Library/pnpm/bin/pnpm"

# Fallback pnpm locations
if [ ! -x "$PNPM_BIN" ]; then
  PNPM_BIN="$(which pnpm 2>/dev/null || echo '')"
fi

if [ -z "$PNPM_BIN" ]; then
  echo "❌  pnpm not found. Install it: curl -fsSL https://get.pnpm.io/install.sh | sh -"
  exit 1
fi

# ── 1. Start MongoDB ──────────────────────────────────────────────────────────
MONGOD="$HOME/mongodb/bin/mongod"
if [ -x "$MONGOD" ]; then
  if ! lsof -i :27017 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "▶  Starting MongoDB..."
    mkdir -p "$HOME/mongodb/data/db" "$HOME/mongodb/logs"
    "$MONGOD" \
      --dbpath "$HOME/mongodb/data/db" \
      --logpath "$HOME/mongodb/logs/mongod.log" \
      --fork \
      --bind_ip 127.0.0.1 \
      --port 27017
    sleep 2
    echo "✓  MongoDB started"
  else
    echo "✓  MongoDB already running on :27017"
  fi
else
  echo "⚠  ~/mongodb/bin/mongod not found — assuming MongoDB is running elsewhere"
fi

# ── 2. Start FastAPI backend ──────────────────────────────────────────────────
BACKEND_DIR="$SCRIPT_DIR/backend"

if [ ! -d "$BACKEND_DIR/venv" ]; then
  echo "❌  Python venv not found. Run:"
  echo "    cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

echo "▶  Starting FastAPI backend on :8000..."
osascript >/dev/null 2>&1 <<OSASCRIPT_EOF || true
tell application "Terminal"
  do script "cd '$BACKEND_DIR' && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
  activate
end tell
OSASCRIPT_EOF

# Fallback for non-macOS or when osascript unavailable
if ! lsof -i :8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "   (Opening backend in background — check terminal for errors)"
  cd "$BACKEND_DIR"
  source venv/bin/activate
  nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$BACKEND_DIR/server.log" 2>&1 &
  BACKEND_PID=$!
  echo "   Backend PID: $BACKEND_PID  (logs: backend/server.log)"
  cd "$SCRIPT_DIR"
fi

sleep 3

# ── 3. Start frontend ─────────────────────────────────────────────────────────
echo "▶  Starting React frontend on :5173..."
osascript >/dev/null 2>&1 <<OSASCRIPT_EOF || true
tell application "Terminal"
  do script "cd '$SCRIPT_DIR' && PORT=5173 BASE_PATH=/ $PNPM_BIN --filter @workspace/kaushalya run dev"
  activate
end tell
OSASCRIPT_EOF

# Fallback
if ! lsof -i :5173 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "   (Starting frontend in background)"
  cd "$SCRIPT_DIR"
  PORT=5173 BASE_PATH=/ "$PNPM_BIN" --filter @workspace/kaushalya run dev > /tmp/kaushalya-frontend.log 2>&1 &
  FE_PID=$!
  echo "   Frontend PID: $FE_PID  (logs: /tmp/kaushalya-frontend.log)"
fi

sleep 4

# ── 4. Print access info ──────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  KAUSHALYA is starting up"
echo "============================================================"
echo ""
echo "  Frontend   →  http://localhost:5173"
echo "  Backend    →  http://localhost:8000"
echo "  Swagger    →  http://localhost:8000/docs"
echo "  Health     →  http://localhost:8000/api/healthz"
echo ""
echo "  Demo Accounts (password: Demo@1234)"
echo "    Trainee    trainee@kaushalya.demo"
echo "    Admin      admin@kaushalya.demo"
echo "    Employer   employer@kaushalya.demo"
echo "    Super Admin superadmin@kaushalya.demo"
echo ""
echo "  To seed the database:"
echo "    cd backend && source venv/bin/activate && python scripts/seed_database.py"
echo ""
echo "============================================================"
