---
name: adjudication-rationale
description: Produce clause-grounded, reviewable claims adjudication reasoning for coverage and settlement recommendations.
---

# Adjudication Rationale

Use this Skill when the agent is asked to explain *why* a claim appears covered, not covered,
conditional, or ready for referral.

## Required analysis order

1. Confirm the policy form, insured risk, and relevant period.
2. Identify the insuring agreement or coverage grant that could respond.
3. Test relevant definitions and endorsements.
4. Test exclusions and carve-backs.
5. Test conditions, duties after loss, and other prerequisites.
6. Apply excesses, deductibles, sub-limits, and overall limits.
7. Identify any missing evidence, ambiguity, or referral trigger.

## Required output structure

Return:

- **Recommendation** - Covered, Not covered, Conditional, or Refer
- **Confidence** - percentage or qualitative confidence
- **Policy basis** - the relevant sections or evidence relied on
- **Application to facts** - how each key fact affects the outcome
- **Financial treatment** - gross amount, deductions, and provisional net amount if known
- **Evidence gaps** - what is still needed
- **Human review** - who should approve or review the outcome

## Guardrails

- Do not invent policy wording or quote text that wasn't provided.
- If clauses conflict or evidence is incomplete, prefer **Refer**.
- Distinguish facts from assumptions.
- Treat the output as decision support, not a final claim determination.
