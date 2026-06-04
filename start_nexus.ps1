# Nexus AI — Windows startup
$ErrorActionPreference = "Stop"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
if (-not (Test-Path "venv")) { python -m venv venv }
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt -q
if (-not (Test-Path "data/demo/crm_data.json")) {
    python scripts/generate_demo_data.py --seed 42
}
Start-Process -NoNewWindow uvicorn -ArgumentList "backend.main:app","--reload","--port","8000"
Write-Host "API: http://localhost:8000  Dashboard: http://localhost:3000 (run frontend separately)"
