#!/usr/bin/env python3
"""Validate a clean-clone dev environment before demo or CI."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_PYTHON = (3, 11)
REC_PYTHON = (3, 11, 3, 12)


def _check_python() -> list[str]:
    errors: list[str] = []
    v = sys.version_info[:3]
    if v[:2] < MIN_PYTHON:
        errors.append(
            f"Python {v[0]}.{v[1]} is too old; need >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
        )
    elif v[:2] > (3, 12):
        print(
            "note: Python 3.13+ — use demo-only install (requirements.txt) or Docker; "
            "for ChromaDB also install requirements-vector.txt on Python 3.11–3.12"
        )
    return errors


def _check_files() -> list[str]:
    errors: list[str] = []
    for rel in (".env.example", "requirements.txt", "data/demo/crm_data.json"):
        if not (ROOT / rel).exists():
            errors.append(f"Missing {rel} — run: python scripts/generate_demo_data.py --seed 42")
    if not (ROOT / ".env").exists():
        print("warn: .env not found — copy from .env.example")
    return errors


def _check_imports() -> list[str]:
    errors: list[str] = []
    for mod in ("fastapi", "pydantic", "pytest", "networkx"):
        if importlib.util.find_spec(mod) is None:
            errors.append(f"Python package not installed: {mod} (pip install -r requirements.txt)")
    if importlib.util.find_spec("chromadb") is None:
        print("warn: chromadb not installed — demo mode uses in-memory vector fallback")
    return errors


def _check_pilot_profile() -> list[str]:
    """Fail if default secrets or demo-trust settings remain (customer pilot deploy)."""
    errors: list[str] = []
    sys.path.insert(0, str(ROOT))
    try:
        from backend.config import NexusConfig

        cfg = NexusConfig()
    except Exception as exc:
        return [f"Could not load NexusConfig: {exc}"]

    if cfg.nexus_api_key == "demo-key":
        errors.append("Rotate NEXUS_API_KEY — still using demo-key")
    weak_jwt = cfg.jwt_secret in ("change-me", "change-me-in-production", "")
    if weak_jwt or len(cfg.jwt_secret) < 32:
        errors.append("Rotate JWT_SECRET to a unique value (min 32 characters)")
    if not cfg.nexus_pre_live_mode:
        errors.append("Set NEXUS_PRE_LIVE_MODE=true for paid pilot")
    if cfg.auth_mode != "jwt_required":
        errors.append("Set AUTH_MODE=jwt_required for paid pilot")
    if not cfg.nexus_ws_require_auth:
        errors.append("Set NEXUS_WS_REQUIRE_AUTH=true for paid pilot")
    if cfg.trust_client_role():
        errors.append("Set NEXUS_TRUST_CLIENT_ROLE=false for paid pilot")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Nexus AI environment")
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="Enforce paid-pilot security profile (rotated secrets, pre-live auth)",
    )
    args = parser.parse_args()

    print("Nexus AI setup verification")
    print(f"  root: {ROOT}")
    print(f"  python: {sys.version.split()[0]}")
    if args.pilot:
        print("  mode: pilot profile check")

    errors = _check_python() + _check_files() + _check_imports()
    if args.pilot:
        errors += _check_pilot_profile()

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(f"  - {e}")
        if args.pilot:
            print("\nSee docs/pilot.env.example and docs/MARKET_READY.md")
        return 1
    print("\nOK — environment looks ready for pytest and uvicorn.")
    if args.pilot:
        print("OK — pilot security profile checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
