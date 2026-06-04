# Nexus AI — Market-ready product strategy

**Version:** 1.0 · June 2026  
**Status:** **Pilot ready** (synthetic / webhook data) — not beta or production  
**ICP:** Mid-market B2B CFO offices ($50M–$300M revenue) approving vendor wires and credit weekly

This document is the commercial and product north star. Code wins over marketing. See [CTO_HANDOFF.md](CTO_HANDOFF.md) for technical inventory.

---

## One sentence

**Pre-release risk review before you wire** — cross-source gaps, stress-tested, traced to prior losses, with an audit trail.

---

## Sellable workflow

| Step | Buyer language | Product surface |
|------|----------------|-----------------|
| 1 | Connect sources | `/integrations` |
| 2 | Run review | `/` → **Run risk review** |
| 3 | Sign-off findings | Findings + `/decisions` |
| 4 | Audit replay | `/traceback` + `GET /api/v1/audit/verify` |
| 5 | Export report | **Export JSON** on Risk review page |

**API:** `POST /api/v1/risk-review/run` (analyst+) → `RiskReviewReport` with `data_mode`.

---

## Pilot package (8 weeks)

**Included:** Pre-Release Risk Review, synthetic or HMAC webhook JSON, audit export, dedicated single-tenant deploy, pre-live auth profile (`docs/pilot.env.example`).

**Excluded:** Live Salesforce/NetSuite, SSO, multi-tenant SaaS, evolution auto-apply, SOC2.

**Success:** ≥4 reviews, 1 validated finding, champion replays audit unaided, <15 min per review by week 2.

**Pricing:** Design pilot $0–$15k · Paid $3k–$8k/mo · Enterprise custom — see [PRICING.md](PRICING.md).

---

## Features: keep / hide / defer

| Action | Item |
|--------|------|
| **Keep** | Risk review, findings, traceback, decisions, integrations, audit |
| **Hide** | Agent activity, Evolution (advanced env only) |
| **Defer** | Plugin runtime loader, live CRM/ERP, multi-tenant DB, OTel |
| **Cut from pitch** | “Six-agent platform,” generic copilot |

---

## Trust blockers

| Stage | Blockers |
|-------|----------|
| **Paid pilot** | Rotate secrets, `NEXUS_PRE_LIVE_MODE`, `NEXUS_WS_REQUIRE_AUTH`, dedicated deploy |
| **Beta** | Plaid E2E, live pipeline mode, fail-loud empty connectors |
| **Production** | Tenant isolation, SSO, SOC2, load tests |

Run `python scripts/verify_setup.py --pilot` before customer deploy.

---

## Verdict

| Stage | Ready? |
|-------|--------|
| Design pilot (synthetic/webhook) | **Yes** |
| Paid pilot | **Conditional** (Phase 1 security checklist) |
| Beta (live bank) | **No** |
| Production SaaS | **No** |

**Related:** [GTM_LAUNCH.md](GTM_LAUNCH.md) · [launch-readiness.md](launch-readiness.md) · [PRICING.md](PRICING.md)
