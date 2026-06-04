# GTM launch strategy — Nexus AI (90-day wedge)

**Last updated:** June 2026  
**Verdict:** **Pilot ready** on synthetic data with strict auth profile — not production ready.

This document is the commercial source of truth alongside [launch-readiness.md](launch-readiness.md) and [CTO_HANDOFF.md](CTO_HANDOFF.md).

---

## 1. ICP recommendation

**Initial ICP:** Mid-market **B2B CFO office** — companies with **$50M–$300M revenue**, centralized treasury/FP&A, and **no dedicated quant risk team**.

**Why this segment:**
- They already approve vendor wires, credit lines, and large deal terms weekly.
- Pain is **process and audit**, not alpha — they will pay for defensible review, not “another AI chat.”
- Demo synthetic data (CRM + ERP + bank overlap) maps to their real blind spots: concentration, related-party payments, cash timing.
- Sales cycle is short enough for 90-day closes vs. global banks.

**Do not target (yet):** Hedge funds, retail trading apps, generic “AI platform” buyers, or enterprises requiring SSO + tenant isolation on day one.

---

## 2. First sellable workflow

**Pre-Release Risk Review** — a repeatable review **before** releasing funds or credit:

1. **Ingest** — CRM deals, ERP vendors/payments, bank flows (demo JSON today; Plaid sandbox on pilot).
2. **Detect blind spots** — cross-source gaps (e.g., CFO equity overlap + vendor concentration).
3. **Stress test** — adversarial attacks on each finding (simulation before action).
4. **Trace memory** — link to named historical failures and loss paths in graph memory.
5. **Decide** — structured recommendations (defer wire, review loan, sell/hedge) with audit trail.

**Buyer value in under 2 minutes:** “We catch the Acme-style concentration and circular payment pattern *before* you approve the wire — with a traceable report your auditor can replay.”

**Code entry points:**
- UI: sidebar **Run Risk Review** → `/`
- REST: `POST /api/v1/risk-review/run` (analyst+)
- Platform truth: `GET /api/v1/platform/info`

---

## 3. Buyer / user / champion map

| Role | Title (typical) | Job | Nexus touchpoint |
|------|-----------------|-----|------------------|
| **Buyer** | VP Finance / CFO | Owns cash, credit policy, audit readiness | Signs pilot; cares about report + audit chain |
| **User** | Treasury analyst / FP&A manager | Runs weekly release checklist | Runs risk review, exports findings |
| **Champion** | Head of Internal Audit / Risk | Needs defensible trace, not black box | Traceback graph, `GET /api/v1/audit/verify`, correlation IDs |

**Economic buyer question:** “Will this prevent a $50k–$500k miss before we wire?” — demo narrative targets **$79k circular payment** and **concentration** scenarios.

---

## 4. Features — keep, cut, defer, hide

| Action | Item | Rationale |
|--------|------|-----------|
| **Keep** | Pre-Release Risk Review workflow | Single revenue story |
| **Keep** | Blind spots, adversarial, traceback, decisions | Core differentiated loop |
| **Keep** | Audit log + pipeline correlation | Trust / enterprise narrative |
| **Keep** | Connections page + capability API | Shows path to live data |
| **Hide** | Agents raw view, Evolution UI | `NEXT_PUBLIC_SHOW_ADVANCED=true` only |
| **Defer** | Evolution auto-apply / weight changes | Roadmap; approval UI not shipped |
| **Defer** | Live CRM/ERP/news vendors | Missing integrations |
| **Defer** | Multi-tenant DB isolation | Header-scoped only today |
| **Defer** | OTel / Prometheus | Planned |
| **Cut from pitch** | “Multi-agent platform,” generic dashboard | Replaced by Risk Review language |
| **Cut from prod claims** | Client-trusted `X-Nexus-Role` | Off in pre-live profile |

---

## 5. Gaps blocking a real sale

| Blocker | Status | Mitigation |
|---------|--------|------------|
| Synthetic-only data in default demo | **Open** | Pilot profile + Plaid sandbox path |
| No per-tenant DB isolation | **Open** | Single-tenant pilot contract + dedicated deploy |
| Default secrets (`demo-key`, `change-me`) | **Open** | `docs/pilot.env.example` + pre-flight script |
| JWT not required by default | **Open** | Pre-live profile for design partners |
| Live CRM/ERP/news | **Missing** | Webhook ingest HMAC for customer ETL |
| SSO / SCIM | **Missing** | Enterprise tier roadmap |
| SOC2 / pen test | **Missing** | Pilot under NDA + shared responsibility |
| Evolution approval | **Stub** | Hide from v1 nav |

---

## 6. Pricing and packaging

See [PRICING.md](PRICING.md). Summary:

| Tier | Price signal | Includes |
|------|--------------|----------|
| **Design pilot** | $0–$15k / 8 weeks | Synthetic or sandbox, 1 workflow, audit export |
| **Paid** | $3k–$8k / mo | Risk reviews + 2 connectors + JWT RBAC |
| **Enterprise** | Custom | Dedicated deploy, SSO roadmap, SLA, live connectors |

Price on **reviews and connectors**, not token usage.

---

## 7. Code-backed differentiators

| Claim | Evidence | Generic? |
|-------|----------|----------|
| Simulation before action | `backend/agents/adversarial.py` | **Differentiated** |
| Traceable memory | `backend/memory/graph.py`, `demo_graph.py`, traceback agent | **Differentiated** |
| Auditable decisions | `backend/utils/pipeline_trace.py`, `data/audit.jsonl`, hash verify | **Differentiated** |
| Connector abstraction | `backend/integration/capabilities.py`, `data_mode` per source | **Moat over time** |
| Structured risk artifact | `POST /api/v1/risk-review/run`, `backend/services/risk_review.py` | **Differentiated** |
| Six-agent orchestration | `backend/agents/orchestrator.py` | Implementation detail — don’t lead with it |
| “AI chat” | LLM streams in agents | **Generic** — de-emphasize |

---

## 8. Top trust risks (customer perspective)

1. **Demo data mistaken for live** — mitigate with `data_mode` on reports and platform info.
2. **Role spoofing via headers** — mitigate with `NEXUS_PRE_LIVE_MODE=true` for pilots.
3. **Shared memory across tenants** — disclose; single-tenant deploy for paid pilots.
4. **Black-box LLM** — decisions are rule-based in demo; show chain_of_thought + audit events.
5. **Evolution changing weights without approval** — hidden in v1; `approval_required: true` in schema.
6. **Default credentials in production** — blocked by pilot checklist.

---

## 9. Prioritized implementation plan (90 days)

### Days 1–30 — Close narrative + pilot profile
- [x] Risk Review workflow UI + API
- [x] Platform info + pilot env template
- [x] GTM docs aligned to code
- [ ] First design partner LOI with synthetic pilot
- [ ] Rotate secrets + pre-live profile on staging

### Days 31–60 — First live path
- [ ] Plaid sandbox connector validated end-to-end (`NEXUS_DEMO_MODE=false`)
- [ ] Customer webhook ingest for ERP CSV/JSON
- [ ] PDF/JSON export of `RiskReviewReport`
- [ ] Gateway RBAC doc + example (nginx/API gateway)

### Days 61–90 — Paid conversion
- [ ] Dedicated single-tenant deploy template (persistent volumes)
- [ ] Decision outcome feedback loop (shipped API; wire to evolution roadmap)
- [ ] Security questionnaire template
- [ ] Beta verdict: live connector + staging auth hardening

---

## 10. Launch readiness verdict

| Stage | Ready? | Notes |
|-------|--------|-------|
| First revenue (design pilot) | **Yes** | Synthetic + audit + Risk Review API |
| Paid pilot (external) | **Conditional** | Requires pre-live profile + secret rotation |
| Beta (live data) | **No** | Plaid path stub-validated only |
| Production | **No** | No tenant isolation, SSO, or OTel |

**Overall: Pilot ready** — suitable to sell **8-week design pilots** to mid-market CFO offices on the Pre-Release Risk Review workflow. Not beta or production ready until live connector + auth hardening checklist in [launch-readiness.md](launch-readiness.md) is met.

---

## Related docs

- [PRICING.md](PRICING.md)
- [pilot.env.example](pilot.env.example)
- [CTO_HANDOFF.md](CTO_HANDOFF.md)
- [launch-readiness.md](launch-readiness.md)
