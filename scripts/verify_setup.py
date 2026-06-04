#!/usr/bin/env python3
"""Validate a clean-clone dev environment before demo or CI."""
from __future__ import annotations

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


def main() -> int:
    print("Nexus AI setup verification")
    print(f"  root: {ROOT}")
    print(f"  python: {sys.version.split()[0]}")
    errors = _check_python() + _check_files() + _check_imports()
    if errors:
        print("\nFAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nOK — environment looks ready for pytest and uvicorn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
