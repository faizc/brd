---
name: brd-builder
description: |
  Turns a rough business idea into a technology-agnostic Business Requirements
  Document (BRD) by interviewing the user about objectives, quantified benefits,
  current process steps, actors, existing systems and per-step pain points, then
  researching benchmarks and producing the BRD.
  Use when the user says "turn my idea into a BRD", "create a business requirements
  document", "document this business process", "capture requirements for this use
  case", "build a BRD for", or "help me define the business case".
  Do NOT use for solution architecture, technical design or HLD/LLD documents, RFPs,
  or project status updates — this skill deliberately stops before technology choices.
---

## Overview

This skill converts an idea into a **business** requirements document — problem, process,
people, pain, and measurable impact. It is explicitly **solution-agnostic**: no architecture,
no product names, no technology recommendations, even if the user hints at one. It works by
structured interview (6 discovery rounds), then independent research to benchmark and
sanity-check the numbers, then generates the BRD.

## When to Use

- User has an idea, pain point or opportunity and needs it written up for business stakeholders
- User needs the "as-is" process documented with actors, systems and step timings
- User needs a business case with quantified baseline and target metrics
- User needs a BRD before any solutioning / design work starts

## When NOT to Use

- Technical design, architecture, or solution options — out of scope by design
- Sizing, pricing, or vendor selection — out of scope
- A status report on an in-flight project
- A one-line summary of an idea — a BRD is a multi-round interview; don't invoke for trivia

## Quick Start

```
User: "I want to fix our invoice approval delays — turn this into a BRD."
1. Check existing knowledge sources for prior context on the idea
2. Round 1 objective → Round 2 quantify → Round 3 as-is steps → Round 4 actors
   → Round 5 systems/data → Round 6 re-walk measuring the objective's dimension
3. Research benchmarks and compute the gap, showing the arithmetic
4. Fill references/brd-template.md section by section
5. Deliver the BRD plus the list of open questions
```

## Core Instructions

### Golden rule — stay above the technology line

Never name a product, platform, service, architecture pattern or automation approach in the
BRD or in your questions. If the user proposes one ("we'll use a portal / RPA / an app"),
record it verbatim in **Appendix B: Ideas Parked for Solutioning** and reply: "Noted — I've
parked that for the design phase; let's finish defining the business need first."
Every requirement must be phrased as an outcome ("approval decision must be recorded within
4 hours"), never as a mechanism ("build an approval app"). Naming systems the business uses
TODAY is allowed and required in the as-is sections — that is documentation, not solutioning.

### Step 1 — Ground before you ask

Check the agent's connected knowledge sources for existing context on the idea — prior BRDs,
process documentation, audit findings — so you don't ask what you can look up. Summarize what
you found in one line and confirm it with the user.

### Step 2 — Run the six discovery rounds

Ask **one round at a time**, max 3-4 questions per turn, always offering a "not sure / help me
estimate" option. After each round, echo back a compact summary and ask the user to correct it
before moving on. Full question bank with follow-ups and good/bad answer examples:
[references/discovery-questions.md](references/discovery-questions.md).

1. **Business objective** — what pain exists today, or what benefit is envisioned? Who feels it?
   What triggered it now? What is the cost of doing nothing?
2. **Quantification** — can it be measured? Capture baseline value, unit, target, deadline and
   source of truth. If the user can't quantify, agree a proxy metric, mark it
   `[Assumption — to validate]`, and record what must be sampled to establish a real baseline.
3. **Current process (as-is)** — walk the workflow end to end, step by step, in business
   language. Capture trigger, steps, decision points, exceptions/rework loops, and end state.
   Read the steps back numbered and ask what happens BETWEEN steps — that is where hidden
   handoffs and queues live.
4. **Actors per step** — the business role (not the person's name) performing each step, plus
   who approves, who is consulted, who is informed. Note volumes, and single points of failure.
5. **Systems, applications and datasets per step** — what each actor touches at that step:
   system of record, spreadsheets, email, paper, portals; which data is read vs. created;
   where handoffs are manual; sensitivity or compliance classification.
6. **Pain-point-driven re-walk (the critical round)** — re-walk the same workflow through the
   lens of the objective from round 1, and quantify the dimension that matters:
   - Cycle-time objective → elapsed + touch time per step, wait/queue time, which step blows
     the deadline, and the fastest case ever and why it differed
   - Cost objective → effort (person-minutes) and loaded cost per step, volume × unit cost,
     which steps are pure coordination
   - Quality/compliance objective → error/exception rate per step, rework %, audit findings
   - Experience objective → handoffs, re-keying, customer touchpoints per step
   Close by presenting the step table with a total row, stating the gap ("today X vs. required
   Y, gap Z"), and confirming the top 3 constraining steps with the user.

### Step 3 — Independent research

Only after the interview, gather industry benchmarks for the metric in question, typical
regulatory or compliance drivers, and comparable published outcomes. Every researched claim
needs a publisher, title and date inline. Keep researched benchmarks in a separate column from
the user's own figures — never merge them, and never present a benchmark as the user's number.

### Step 4 — Validate the numbers

State the formula and inputs beneath every derived figure (totals, %, gaps, annualized impact).
Do not present a number you cannot show the arithmetic for. Mark unverified inputs `[Assumption]`.

### Step 5 — Generate the BRD

Fill [references/brd-template.md](references/brd-template.md) section by section. Sections, in
order: Document Control · Executive Summary · Business Objective · Scope (In/Out) · Current
Business Process (As-Is) · Users & Actors (Business Roles) · Systems, Applications and Datasets
Involved · Key Pain Points (quantified, per step) · Business Requirements · Expected Business
Impact · Assumptions, Constraints & Dependencies · Success Metrics & Measurement Plan · Risks ·
Open Questions · Approvals · Appendix A: Research & Benchmarks · Appendix B: Ideas Parked for
Solutioning · Appendix C: Glossary · Appendix D: Interview Log.

Any section the interview did not cover ships as `[To be confirmed — <what is needed and from
whom>]`. Never fill a gap with invented facts.

### Step 6 — Close the loop

After delivering, list the open questions the user must resolve and offer a stakeholder review
summary, a short readout, or a second pass once the open items are answered.

## Output

- The BRD document, 4-10 pages
- A 5-line chat summary: objective, baseline → target metric, top 3 pain points, open questions count
- Process, actors and systems presented as tables; step timings as a table with elapsed vs.
  touch time and a total row

## Guardrails

- **No technology solutioning** anywhere in the BRD — park it in Appendix B instead.
- **Never fabricate** metrics, volumes, timings, system names, role names or benchmarks.
  Unknown → `[To be confirmed]`; estimated → `[Assumption]` with who must validate it.
- Ask one round at a time; never dump all 20+ questions in a single turn.
- Use business roles, not individuals' names — never assess any named person's performance.
- Research claims carry a named source and date.
- Do not send or distribute the BRD to anyone unless explicitly asked.
