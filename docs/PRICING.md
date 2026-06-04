# Pricing and packaging — Nexus AI

Pricing is tied to **business risk avoided**, not LLM tokens.

## Tiers

### Design pilot — $0 to $15,000 one-time (8 weeks)

**For:** First 3–5 design partners in the mid-market CFO ICP.

**Includes:**
- Pre-Release Risk Review workflow (UI + API)
- Synthetic data **or** customer-provided JSON via HMAC webhooks
- Audit log export + hash verification
- Weekly review session with product team

**Excludes:** Live CRM vendors, SSO, SLA, dedicated infrastructure.

**Success metric:** Champion replays one audit trail without engineering help.

---

### Paid — $3,000–$8,000 / month

**For:** CFO office running weekly release reviews.

**Includes:**
- Unlimited risk reviews (fair use rate limits)
- **2 live connectors** (e.g., Plaid sandbox → production, webhook ERP)
- JWT RBAC (`viewer` / `analyst` / `admin`)
- Pre-live or staging auth profile
- Email support, 99.5% target uptime on dedicated single-tenant deploy

**Add-ons:**
- Additional connector: $500–$1,500 / mo each
- Extra tenant/environment: $1,000 / mo

---

### Enterprise — custom annual contract

**For:** $300M+ revenue or regulated industries.

**Includes (roadmap-backed — confirm in SOW):**
- Dedicated VPC / single-tenant isolation
- SSO (SAML/OIDC) — **planned**
- Custom retention + SIEM export
- SLA 99.9%, named CSM
- Security review support

**Not included until shipped:** Multi-tenant SaaS isolation, SOC2 Type II report.

---

## What belongs in paid vs roadmap

| Paid tier (now) | Roadmap |
|-----------------|---------|
| Risk Review API + audit | Evolution auto-apply |
| Plaid / webhook ingest | Salesforce, NetSuite native |
| JWT + RBAC | SSO / SCIM |
| Traceback + graph memory | Cross-customer benchmarking |
| Decision outcome API | OTel dashboards |

---

## Packaging principle

Sell **one workflow** (“Pre-Release Risk Review before wires/credit”), not “six agents.” Expansion revenue comes from **connectors and review volume**, not model upgrades.
