# Discovery Question Bank

Six rounds. Ask one round at a time (3-4 questions max per card), always include a
"not sure — help me estimate" option, and always echo back what you captured before moving on.
Never ask a question whose answer you can look up in the user's own email, files or calendar.

**Interview discipline**
- Ask *how work happens*, never *how it should be built*.
- If an answer is a solution ("we need a portal"), ask the un-solutioning question:
  *"What would that let you do that you can't do today?"* — then record the answer as the need
  and park the solution in Appendix B.
- Chase every number to a source: system report, sample, or someone's estimate. Label accordingly.
- Stop a round when you have enough to fill the corresponding template section, not when the
  question bank is exhausted.

---

## Round 1 — Business objective

1. In one sentence, what is the problem today or the benefit you're after?
2. Is this driven by a pain point, an envisioned benefit, or a compliance/regulatory mandate?
3. Who feels this most — which roles, and which customers or downstream teams?
4. What triggered this now (audit, escalation, growth, deadline, cost pressure)?
5. What happens if nothing changes in the next 12 months?

*Good answer:* "Supplier invoices take ~3 days to approve; our contract terms require 24 hours
and we're paying late fees."
*Needs a follow-up:* "We want to be more efficient." → *Efficient at what, for whom, measured how?*

## Round 2 — Quantification

1. What metric best expresses the objective — time, cost, effort, error rate, volume, satisfaction?
2. What is it today (baseline)? Where does that number come from?
3. What must it become, and by when? Who set that target — internal goal or external mandate?
4. What volume does this apply to (transactions per day/month, peak vs. average)?
5. What does one unit of failure cost (late fee, penalty, rework, lost deal, escalation)?

*If they can't quantify:* offer a proxy ("number of chase-up emails per case", "count of
exceptions raised per month"), note it as `[Assumption — to validate]`, and record what
must be sampled or instrumented to establish a real baseline.

## Round 3 — Current business process (as-is)

1. What starts this process, and what marks it as finished?
2. Walk me through it step by step — what happens first, then what?
3. Where are the decision points, and what are the possible outcomes at each?
4. What happens on the exception path — rejections, missing information, disputes?
5. How often does the process loop back or get redone?
6. Does the process differ by region, business unit, value threshold or transaction type?

*Technique:* read the steps back as a numbered list and ask "what's missing between step 3
and step 4?" — that is where undocumented handoffs and queues hide.

## Round 4 — Actors per step

1. For each step, which business role performs it? (Role, not the individual's name.)
2. Who approves, who is consulted, who just needs to be informed?
3. How many people hold each role, and how much of their week does this consume?
4. Are any steps done by a partner, vendor, shared-service centre or offshore team?
5. Which roles are single points of failure (one person, one shift, one location)?
6. Where does work sit waiting because the right role isn't available?

## Round 5 — Systems, applications and datasets per step

1. At each step, what does the actor open or touch — system, spreadsheet, email, portal, paper?
2. Which one is the system of record for the transaction?
3. What data do they read at that step, and what do they create or change?
4. Where is the same information typed in more than once?
5. How does work move between steps — automatically, by email, by file, by phone, by hand?
6. Which data is late, incomplete, or has to be reconciled before it can be used?
7. Any sensitivity or compliance classification on this data (personal, financial, regulated)?

## Round 6 — Pain-point-driven re-walk (the differentiating round)

Re-walk the *same* step list from Round 3, measuring the dimension that matters to Round 1.

**If the objective is cycle time**
1. For each step: how long does it actually take once someone starts it (touch time)?
2. How long does it sit waiting before someone starts it (queue/wait time)?
3. Which step most often blows the deadline, and why?
4. What is the fastest this has ever completed, and what made that case different?

**If the objective is cost or effort**
1. Effort per step in person-minutes, and the role's loaded cost?
2. Volume per month × effort = monthly effort; where is the concentration?
3. Which steps are pure coordination (chasing, forwarding, status-checking)?

**If the objective is quality or compliance**
1. Error or exception rate per step, and how errors are detected — and by whom?
2. What proportion of cases require rework, and at which step is it caught?
3. What have audits or regulators flagged, and against which step?
4. What evidence must be retained, and is it captured today?

**If the objective is experience (employee or customer)**
1. How many handoffs and how many times is the customer asked for the same thing?
2. Where do people complain, escalate, or work around the process?
3. Which step do the people doing the work say they hate most, and why?

**Close the round**
- Present the step table with the measured column filled and a total row.
- State the gap: "today `<X>` vs. required `<Y>` → the gap is `<Z>`."
- Confirm the top 3 constraining steps with the user before writing the BRD.
