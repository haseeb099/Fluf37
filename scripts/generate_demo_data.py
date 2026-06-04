#!/usr/bin/env python3
"""
NEXUS AI — Synthetic Demo Data Generator
Generates reproducible synthetic financial data with hidden patterns.
Usage: python scripts/generate_demo_data.py --seed 42
"""
import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_demo_data(seed: int = 42):
    rng = random.Random(seed)
    base_date = datetime(2026, 5, 1)

    def days_ago(n):
        return (base_date - timedelta(days=n)).isoformat() + "Z"

    # ── CRM Data ─────────────────────────────────────────────────
    crm_data = {
        "deals": [
            {
                "id": "deal_001",
                "company": "Acme Corp",
                "contact_name": "James Chen",
                "contact_role": "CFO",
                "deal_value": 450000,
                "stage": "contract_sent",
                "payment_terms_days": 90,
                "expected_close": days_ago(-15),
                "equity_holders": [
                    {"name": "James Chen", "equity_pct": 40.0},
                    {"name": "Sarah Williams", "equity_pct": 25.0},
                ],
                "notes": "Large deal, expedited review requested by CFO",
                "is_at_risk": True,
                "risk_reason": "Payment terms misalignment with cash flow",
            },
            {
                "id": "deal_002",
                "company": "Beta Industries",
                "contact_name": "Maria Santos",
                "contact_role": "Procurement",
                "deal_value": 125000,
                "stage": "negotiation",
                "payment_terms_days": 30,
                "expected_close": days_ago(-5),
                "equity_holders": [],
                "notes": "Standard deal, no issues",
                "is_at_risk": False,
                "risk_reason": None,
            },
            {
                "id": "deal_005",
                "company": "Epsilon Tech",
                "contact_name": "James Chen",
                "contact_role": "Board Advisor",
                "deal_value": 230000,
                "stage": "proposal_sent",
                "payment_terms_days": 60,
                "expected_close": days_ago(-20),
                "equity_holders": [{"name": "James Chen", "equity_pct": 12.5}],
                "notes": "Referred by Acme Corp",
                "is_at_risk": True,
                "risk_reason": "Concentration risk: same key person as Acme deal",
            },
        ],
        "contacts": [
            {
                "id": "c_001",
                "name": "James Chen",
                "email": "j.chen@acmecorp.com",
                "companies": ["Acme Corp", "Epsilon Tech"],
                "equity_exposure": 52.5,
            },
        ],
        "generated_at": base_date.isoformat(),
        "seed": seed,
    }

    # ── ERP Data (cross-source with CRM + bank) ───────────────────
    erp_data = {
        "vendors": [
            {
                "id": "vendor_001",
                "name": "Supplier X Ltd",
                "crm_entity_id": "deal_001",
                "total_paid_ytd": 285000,
                "pct_of_total_spend": 0.34,
                "payment_terms_days": 30,
                "linked_bank_entity": "ext_supplier_x",
            },
            {
                "id": "vendor_002",
                "name": "Nexus Holdings LLC",
                "crm_entity_id": None,
                "total_paid_ytd": 335000,
                "pct_of_total_spend": 0.41,
                "payment_terms_days": 0,
                "linked_bank_entity": "ext_shell_001",
                "incorporated_days_ago": 3,
            },
        ],
        "gl_snapshots": [
            {
                "id": "gl_001",
                "account": "cash_operating",
                "balance": 1250000,
                "as_of": days_ago(0),
                "projected_30d_outflow": 195000,
                "projected_30d_inflow": 67000,
                "notes": "30-day cash gap aligns with Acme 90-day terms",
            }
        ],
        "vendor_payments": [
            {
                "id": "vp_001",
                "vendor_id": "vendor_001",
                "amount": 85000,
                "timestamp": days_ago(15),
                "crm_deal_id": "deal_001",
            },
            {
                "id": "vp_002",
                "vendor_id": "vendor_002",
                "amount": 250000,
                "timestamp": days_ago(2),
                "crm_deal_id": None,
            },
        ],
        "generated_at": base_date.isoformat(),
        "seed": seed,
    }

    # ── Bank Data ─────────────────────────────────────────────────
    bank_data = {
        "accounts": [
            {"id": "acc_001", "name": "Operating Account", "balance": 1250000, "type": "checking"},
        ],
        "transactions": [
            {
                "id": "tx_010",
                "amount": 85000,
                "from_account": "ext_acme_001",
                "to_entity": "Supplier X Ltd",
                "to_account": "ext_supplier_x",
                "timestamp": days_ago(15),
                "category": "vendor_payment",
                "description": "Supply chain payment Q2",
                "is_flagged": False,
            },
            {
                "id": "tx_011",
                "amount": 82000,
                "from_account": "ext_supplier_x",
                "to_entity": "Nexus Holdings LLC",
                "to_account": "ext_shell_001",
                "timestamp": days_ago(14),
                "category": "intercompany",
                "description": "Management fee",
                "is_flagged": False,
            },
            {
                "id": "tx_012",
                "amount": 79000,
                "from_account": "ext_shell_001",
                "to_entity": "Acme Corp",
                "to_account": "ext_acme_001",
                "timestamp": days_ago(13),
                "category": "receivable",
                "description": "Commission payment",
                "is_flagged": False,
            },
            {
                "id": "tx_030",
                "amount": 250000,
                "from_account": "acc_001",
                "to_entity": "Nexus Holdings LLC",
                "to_account": "ext_shell_001",
                "timestamp": days_ago(2),
                "category": "vendor_payment",
                "description": "Consulting services",
                "is_flagged": False,
            },
        ],
        "cash_flow_forecast": {
            "30_day_projected_inflow": 67000,
            "30_day_projected_outflow": 195000,
            "gap": -128000,
            "note": "Acme Corp $450k deal on 90-day terms creates cash flow gap",
        },
        "generated_at": base_date.isoformat(),
        "seed": seed,
    }

    trading_data = {
        "positions": [
            {
                "ticker": "ACME",
                "qty": 5000,
                "entry_price": 142.50,
                "current_price": 138.20,
                "pnl": -21500,
                "order_book_imbalance": -0.32,
                "rsi": 32,
                "macd_signal": -0.8,
                "volume_20d_avg": 850000,
                "volume_today": 2100000,
                "pre_earnings": False,
            },
        ],
        "market_data": {"date": base_date.isoformat(), "vix": 18.5},
        "generated_at": base_date.isoformat(),
        "seed": seed,
    }

    news_data = {
        "articles": [
            {
                "id": "news_001",
                "headline": "Acme Corp CFO Under SEC Scrutiny Over Related-Party Transactions",
                "body": "SEC inquiry into James Chen equity positions.",
                "source": "Financial Times",
                "timestamp": days_ago(5),
                "sentiment": -0.72,
                "entities": ["Acme Corp", "James Chen", "SEC"],
                "relevance_score": 0.95,
            },
        ],
        "generated_at": base_date.isoformat(),
        "seed": seed,
    }

    attack_library = {
        "version": "v1",
        "generated_at": base_date.isoformat(),
        "attacks": [
            {
                "id": "lib_atk_001",
                "name": "3-Hop Circular Payment Loop",
                "type": "fraud",
                "description": "Route funds through 3 entities",
                "success_rate_historical": 0.89,
                "detection_difficulty": "high",
                "proposed_defense": "Graph traversal within 7 hops",
            },
        ],
    }

    output_dir = Path("data/demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    attack_dir = Path("data/attack_library")
    attack_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "data/demo/crm_data.json": crm_data,
        "data/demo/erp_data.json": erp_data,
        "data/demo/bank_data.json": bank_data,
        "data/demo/trading_data.json": trading_data,
        "data/demo/news_data.json": news_data,
        "data/attack_library/v1.json": attack_library,
    }

    for path, data in files.items():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"  Generated {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(f"Generating demo data (seed={args.seed})...")
    generate_demo_data(seed=args.seed)
    print("Done.")
