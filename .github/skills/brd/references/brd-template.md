# Business Requirements Document (BRD) — Template

> Technology-agnostic by design. No product, platform, architecture or automation approach
> appears anywhere except Appendix B. Replace every `<…>` placeholder. Keep `[To be confirmed]`
> and `[Assumption]` markers visible in the delivered document — they are features, not gaps.

---

## Document Control

| Field | Value |
|---|---|
| Use Case Title | `<short outcome-based title, e.g. "Reduce supplier invoice approval cycle to under 24 hours">` |
| Document Owner | `<name, role>` |
| Business Sponsor | `<name, role>` |
| Version / Date | `<v0.1 / YYYY-MM-DD>` |
| Status | Draft / In Review / Approved |
| Contributors Interviewed | `<roles and dates>` |

---

## 1. Executive Summary

`<5-8 lines: what business problem or opportunity, who it affects, how big it is today,
what "good" looks like, and what decision is being asked of the reader. No solution.>`

---

## 2. Business Objective

**Objective statement:** `<one sentence, outcome-phrased>`

**Driver type:** Pain point today ☐ · Envisioned benefit ☐ · Regulatory/compliance mandate ☐ · Both ☐

**Why now:** `<trigger — audit finding, growth, cost pressure, deadline, customer escalation>`

**Quantified objective**

| # | Objective | Metric | Baseline today | Source of baseline | Target | Target date | Confidence |
|---|---|---|---|---|---|---|---|
| O1 | `<e.g. cut approval cycle time>` | `<days end-to-end>` | `<3.2 days>` | `<system report / manual sample / [Assumption]>` | `<< 1 day>` | `<Q3 FY27>` | High/Med/Low |
| O2 | | | | | | | |

**If not quantifiable today:** `<proxy metric chosen, why, and the measurement that must be
put in place to establish the baseline — [To be confirmed by <role>]>`

---

## 3. Scope

| In scope | Out of scope |
|---|---|
| `<processes, regions, business units, transaction types>` | `<explicitly excluded, with reason>` |

**Geography / entity coverage:** `<…>` · **Volume covered:** `<transactions per month>`

---

## 4. Current Business Process (As-Is)

**Process trigger:** `<what starts it>` · **End state:** `<what "done" means>` ·
**Frequency / volume:** `<N per day/month>` · **Peak / seasonality:** `<…>`

### 4.1 Process narrative

`<6-12 line plain-language walkthrough of how the work happens today, including the exception
path and any rework loops.>`

### 4.2 Process steps

| Step | Activity (business language) | Trigger / input | Output | Decision point? | Exception / rework path |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

### 4.3 Handoffs and queues

| From step → To step | Handoff mechanism (as-is) | Typical wait before pickup | Failure mode |
|---|---|---|---|
| | | | |

---

## 5. Users and Actors (Business Roles)

> Roles, never individuals. Include volumes — a role performed by 3 people behaves very
> differently from one performed by 300.

| Actor / business role | Steps involved | Responsibility (R/A/C/I) | Headcount | Frequency of involvement | Location / shift | Notes |
|---|---|---|---|---|---|---|
| | | | | | | |

**Approvers and thresholds:** `<who approves what, at which value/risk threshold>`

**Downstream consumers of the output:** `<roles or functions who depend on this process>`

---

## 6. Systems, Applications and Datasets Involved

> As-is facts only. Naming today's systems is documentation, not solutioning.

| Step | Actor | System / application / artefact | System of record? | Data read | Data created or updated | Access mode (UI / file / email / paper) | Manual re-keying? |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

**Key datasets**

| Dataset | Owner (role/function) | Where it lives today | Refresh / latency | Quality issues observed | Sensitivity / compliance classification |
|---|---|---|---|---|---|

**Integration reality today:** `<which handoffs are automated vs. manual — describe factually>`

---

## 7. Key Pain Points — Quantified Against the Objective

### 7.1 Step-level measurement (dimension chosen to match Section 2)

| Step | Elapsed time | Touch (hands-on) time | Wait / queue time | Effort (FTE-hrs) | Cost | Error / rework rate | Constraint? |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| **Total** | | | | | | | |

**Gap analysis:** current total `<X>` vs. required `<Y>` → gap `<Z>`.
Formula and inputs: `<state explicitly>`.

### 7.2 Pain point register

| ID | Pain point | Where it occurs (step / actor / system) | Evidence & source | Quantified impact | Who feels it | Severity |
|---|---|---|---|---|---|---|
| P1 | | | | | | High/Med/Low |
| P2 | | | | | | |

**Top 3 constraining steps:** `<step numbers + one line each on why>`

**Root causes (business, not technical):** `<e.g. approval threshold forces 4 sign-offs; data
arrives after the decision is due>`

---

## 8. Business Requirements

> Outcome-phrased. Each must be testable and traceable to an objective or pain point.

| ID | Requirement (what the business must be able to do) | Type (Functional / Process / Data / Compliance / Reporting) | Traces to | Priority (MoSCoW) | Acceptance criteria |
|---|---|---|---|---|---|
| BR-01 | | | O1 / P1 | Must | |
| BR-02 | | | | | |

**Non-functional business expectations:** `<availability windows, retention, auditability,
language, accessibility, peak-load tolerance — expressed as business needs>`

---

## 9. Expected Business Impact

| Impact area | Baseline (today) | Expected after | Basis of estimate | Annualized value | Confidence | Beneficiary |
|---|---|---|---|---|---|---|
| Cycle time | | | | | | |
| Cost / effort | | | | | | |
| Quality / compliance | | | | | | |
| Employee or customer experience | | | | | | |
| Revenue / growth | | | | | | |

**Qualitative benefits:** `<…>` · **Cost of doing nothing:** `<…>`

---

## 10. Assumptions, Constraints and Dependencies

| # | Type | Statement | Owner to validate | By when | Impact if wrong |
|---|---|---|---|---|---|
| A1 | Assumption | | | | |
| C1 | Constraint | `<policy, regulation, union agreement, budget, freeze window>` | | | |
| D1 | Dependency | `<another initiative, data availability, org change>` | | | |

---

## 11. Success Metrics and Measurement Plan

| Metric | Definition | Baseline | Target | How measured | Measured by (role) | Cadence | First measurement date |
|---|---|---|---|---|---|---|---|

**Baseline establishment actions:** `<what must be instrumented or sampled before go/no-go>`

---

## 12. Risks

| ID | Risk | Category (Business / Process / Data / People / Compliance) | Likelihood | Impact | Mitigation / owner |
|---|---|---|---|---|---|
| R1 | | | | | |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks which section |
|---|---|---|---|---|
| Q1 | | | | |

---

## 14. Approvals

| Role | Name | Decision | Date |
|---|---|---|---|
| Business Sponsor | | Approve / Reject / Rework | |
| Process Owner | | | |
| Compliance / Risk (if applicable) | | | |

---

## Appendix A — Research and Benchmarks

| # | Finding | Relevance to this use case | Source (publisher, title, date) | User's own figure for comparison |
|---|---|---|---|---|
| B1 | | | | |

> Benchmarks are external context only. They never replace the organization's own baseline.

## Appendix B — Ideas Parked for Solutioning

> Captured verbatim during discovery and intentionally excluded from the requirements above.
> Input to the design phase, not commitments.

| # | Idea raised | Raised by (role) | Related requirement / pain point |
|---|---|---|---|

## Appendix C — Glossary

| Term | Definition |
|---|---|

## Appendix D — Interview Log

| Date | Role(s) interviewed | Sections informed |
|---|---|---|
