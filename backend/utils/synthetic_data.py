"""Load demo JSON into typed SourceData."""
import json
from pathlib import Path
from typing import Any, Dict, List

from backend.schemas.models import (
    BankTransaction,
    CRMDeal,
    EquityHolder,
    ERPRecord,
    ERPVendor,
    FailureRecord,
    GLSnapshot,
    NewsItem,
    SourceData,
    TradingPosition,
    VendorPayment,
)

DEMO_DIR = Path("data/demo")


def _load_json(name: str) -> Dict[str, Any]:
    path = DEMO_DIR / name
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_demo_crm() -> List[CRMDeal]:
    raw = _load_json("crm_data.json")
    deals = []
    for d in raw.get("deals", []):
        holders = [EquityHolder(**h) for h in d.get("equity_holders", [])]
        deals.append(CRMDeal(**{**d, "equity_holders": holders}))
    return deals


def get_demo_bank() -> List[BankTransaction]:
    raw = _load_json("bank_data.json")
    return [BankTransaction(**t) for t in raw.get("transactions", [])]


def get_demo_trading() -> List[TradingPosition]:
    raw = _load_json("trading_data.json")
    return [TradingPosition(**p) for p in raw.get("positions", [])]


def get_demo_news() -> List[NewsItem]:
    raw = _load_json("news_data.json")
    return [NewsItem(**a) for a in raw.get("articles", [])]


def get_demo_erp() -> ERPRecord:
    raw = _load_json("erp_data.json")
    return ERPRecord(
        vendors=[ERPVendor(**v) for v in raw.get("vendors", [])],
        gl_snapshots=[GLSnapshot(**g) for g in raw.get("gl_snapshots", [])],
        vendor_payments=[VendorPayment(**p) for p in raw.get("vendor_payments", [])],
    )


def get_demo_source_data() -> SourceData:
    return SourceData(
        crm=get_demo_crm(),
        bank=get_demo_bank(),
        trading=get_demo_trading(),
        news=get_demo_news(),
        erp=get_demo_erp(),
        source_ids=["crm", "erp", "bank", "trading", "news"],
    )


def get_demo_failures() -> List[FailureRecord]:
    from datetime import datetime
    return [
        FailureRecord(
            id="fail_001",
            description="March 2026: 3-hop circular payment Acme→Supplier X→Shell→Acme. Loss $79k.",
            source_ids=["bank", "crm"],
            dollar_loss=79000,
            timestamp=datetime(2026, 3, 15),
            severity="critical",
        ),
        FailureRecord(
            id="fail_002",
            description="Order book spoofing on ACME: RSI divergence preceded 8% drop.",
            source_ids=["trading", "news"],
            dollar_loss=21500,
            timestamp=datetime(2026, 4, 2),
            severity="high",
        ),
        FailureRecord(
            id="fail_003",
            description="Customer-shareholder overlap undetected on Acme deal until audit.",
            source_ids=["crm"],
            dollar_loss=45000,
            timestamp=datetime(2026, 2, 20),
            severity="high",
        ),
    ]
