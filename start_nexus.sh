#!/bin/bash
# NEXUS AI — Single Command Startup
# Usage: ./scripts/start_nexus.sh [--demo] [--reset]
set -e

DEMO_MODE=${1:-"--demo"}
RESET=${2:-""}

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║          NEXUS AI — STARTING UP           ║"
echo "║    Multi-Agent Financial Intelligence     ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# ── Check prerequisites ──────────────────────────────────────
echo "→ Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 required. Install Python 3.11+"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "ERROR: node required. Install Node.js 18+"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "ERROR: npm required."; exit 1; }

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "  ✓ Python $PYTHON_VERSION"
echo "  ✓ Node $(node --version)"

# ── Setup .env ───────────────────────────────────────────────
if [ ! -f ".env" ]; then
  echo "→ Creating .env from .env.example..."
  cp .env.example .env
  echo "  ✓ .env created (demo mode enabled)"
fi

# ── Python dependencies ──────────────────────────────────────
echo "→ Installing Python dependencies..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install -r requirements.txt -q
echo "  ✓ Python dependencies installed"

# ── Generate demo data ───────────────────────────────────────
if [ "$RESET" = "--reset" ] || [ ! -f "data/demo/crm_data.json" ]; then
  echo "→ Generating synthetic demo data (seed=42)..."
  mkdir -p data/demo data/attack_library data/chroma
  python3 scripts/generate_demo_data.py --seed 42 || python scripts/generate_demo_data.py --seed 42
  echo "  ✓ Demo data generated"
else
  echo "  ✓ Demo data already exists (use --reset to regenerate)"
fi

# ── Start backend ────────────────────────────────────────────
echo "→ Starting FastAPI backend on :8000..."
uvicorn backend.main:app --reload --port 8000 --log-level warning &
BACKEND_PID=$!
echo "  ✓ Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "  ⋯ Waiting for backend..."
for i in {1..30}; do
  if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    echo "  ✓ Backend ready"
    break
  fi
  sleep 1
done

# ── Start frontend ───────────────────────────────────────────
echo "→ Installing frontend dependencies..."
cd frontend
npm install -q
echo "→ Starting Next.js frontend on :3000..."
npm run dev &
FRONTEND_PID=$!
cd ..
echo "  ✓ Frontend PID: $FRONTEND_PID"

# ── Save PIDs for cleanup ────────────────────────────────────
echo "$BACKEND_PID" > .nexus_backend.pid
echo "$FRONTEND_PID" > .nexus_frontend.pid

# ── Done ─────────────────────────────────────────────────────
echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║              NEXUS AI READY               ║"
echo "║                                           ║"
echo "║  Dashboard:  http://localhost:3000        ║"
echo "║  API Docs:   http://localhost:8000/docs   ║"
echo "║  API Key:    demo-key                     ║"
echo "║                                           ║"
echo "║  Press Ctrl+C to stop all services        ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# ── Cleanup on exit ──────────────────────────────────────────
trap cleanup EXIT
cleanup() {
  echo ""
  echo "→ Shutting down NEXUS AI..."
  kill $BACKEND_PID 2>/dev/null
  kill $FRONTEND_PID 2>/dev/null
  rm -f .nexus_backend.pid .nexus_frontend.pid
  echo "  ✓ Shutdown complete"
}

wait
