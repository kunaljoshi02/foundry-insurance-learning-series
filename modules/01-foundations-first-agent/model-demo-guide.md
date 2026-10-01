# Module 01 — Instructor model + live demo guide

**Run time:** 12–16 minutes total: 5–7 minutes of slide-linked context, followed by a separate 7–9-minute live exemplar.

**Purpose:** give the room a working mental model of Microsoft Foundry, then make one deliberately small instruction-only insurance agent. This is the canonical short instructor narrative; use the [demo runbook](demo-runbook.md) for the full click-through and optional scripts.

## Outcome and audience promise

For a mixed business/developer audience, promise a useful first milestone—not a claim decision system: by the end, learners can point to the Foundry project, its chat-model deployment, and a saved `policy-coverage-advisor`, and explain what the agent can and cannot know. Today it uses its instructions and conversation only; tools, Skills/toolboxes, policy retrieval, and orchestration come later.

## Readiness and assets

- The shared public foundation is already deployed; the project and chat-model deployment exist, and the instructor can use the project. See the [foundation README](../../foundation/README.md) and [course prerequisites](../../course/prerequisites.md).
- Have the project name and `chatModelDeploymentName` from the foundation outputs. The portal is `https://ai.azure.com`; sign in with the sandbox identity.
- Open the local [agent instruction file](src/policy-coverage-advisor.instructions.md) and the [presenter slides](slides.md) for the synthetic prompt examples. Keep [lab.md](lab.md) for learner practice, not for this short demo.
- Creating the prompt agent is the portal-first path. `deploy.ps1` is an optional accelerator; `verify.ps1` is read-only. Do not deploy the foundation as part of this lesson.

## Separate slide-linked context segment — 5–7 minutes

Deliver this as a complete framing segment **before** opening the live demo. It is distinct from, and additional to, the minute-by-minute live exemplar below. Its purpose is to give business and developer learners the same platform mental model before they watch an agent being created.

| Context time | Slides | Context to set |
| --- | --- | --- |
| 0:00–1:30 | 1–2 | Set the promise: create a small, testable insurance assistant, not a production claims decision-maker. Preview the route from platform vocabulary to live test. |
| 1:30–3:30 | 3–5 | Explain account → project → deployed model → playground. Distinguish a reusable agent from one prompt response; today's behavior is instructions + model + conversation. |
| 3:30–5:00 | 6–7 | Explain why this prompt agent is the deliberate starting point. Set its synthetic Contoso persona and boundaries: generic education only, no policy lookup or customer-specific promise. |
| 5:00–7:00 (optional) | 8–12 | Tell learners what they will see in the live exemplar, preview the four answer sections, and name the next layers (tools, then grounding). Use the remaining time for a question about what evidence a real coverage determination would need. |

**Bridge into the live demo:** “Now that we know what is—and is not—in this agent, let's create it and test the same boundaries in the playground.”

## Live exemplar — separate 7–9 minutes, minute by minute

| Live-demo time | Instructor action | Narration and visible evidence |
| --- | --- | --- |
| 0:00–1:00 | Open `https://ai.azure.com` and select the pre-existing course project. | “The account is the Azure boundary; this project is our work surface. The named model deployment is what the agent calls. We are creating behavior, not training a model.” |
| 1:00–2:00 | In the project, open **Agents → Create agent → Prompt agent** (labels can change; use the current prompt-agent creation experience). | Point out the deployed chat model in the project. If it is missing, stop before creating the agent; see Troubleshooting. |
| 2:00–4:00 | Enter the name/description below, choose the foundation chat-model deployment, and paste the instruction block. Save/create and open the agent playground. | Visible evidence: saved agent name `policy-coverage-advisor` and selected model. Do not imply a tool, corpus, or customer record is connected. |
| 4:00–6:00 | Submit the kitchen-fire prompt, then the flood prompt below. | Look for plain English, caveats, missing facts, and a next step. The response is model-generated; wording may differ. Ask learners what evidence would be needed for a real decision. |
| 6:00–7:00 | Submit the certainty challenge. | A safe response declines to guarantee payment and routes the final decision to a qualified human. An answer that invents a clause or claims policy access is a prompt-quality issue, not proof of grounding. |
| 7:00–9:00 | Return to Slides 11–12. | Contrast the same model with and without instructions; preview Module 02’s reusable tools/Skills. Leave the agent in place for the next module. |

### Paste-ready synthetic setup and prompts

- **Agent name:** `policy-coverage-advisor`
- **Description:** `Instruction-only insurance coverage advisor for Session 1 of the curriculum.`
- **Model:** the pre-existing foundation chat-model deployment (select by its actual deployment name).

Paste as agent instructions:

```text
You are Policy Coverage Advisor for Contoso Insurance, a calm and concise assistant used for training and demonstration.

Your job is to answer general insurance coverage questions in plain English using only the information in the conversation and these instructions. Do not claim to have reviewed a real policy document, declarations page, endorsement, claim file, or customer record unless the user explicitly provides that information in the chat.

When answering a coverage question, use this structure:
1. Short answer
2. Why it might be covered or not covered
3. What information is still needed
4. Recommended next step

Important guardrails:
- Never guarantee that a claim will be paid.
- Never invent policy clause numbers, limits, deductibles, endorsements, waiting periods, or exclusions.
- Do not pretend to use external tools, web search, or policy grounding.
- If the user asks for a final claim decision, legal advice, regulatory certainty, or customer-specific adjudication, say that a licensed insurance professional or claims handler must confirm.
- Keep the tone professional, empathetic, and easy for both business and technical audiences to follow.

You may provide general examples, but label them clearly as examples rather than confirmed policy terms.
```

Use these synthetic, non-customer-specific prompts one at a time:

```text
Does a standard homeowners policy usually cover damage from a kitchen fire?
```

```text
Would flood damage normally be included in the same policy?
```

```text
Can you confirm this claim will definitely be paid?
```

### What to point out—and what not to claim

Expected visible evidence is a saved named agent, its selected model, and three conversational responses. A good answer says “often” or “it depends,” asks for policy wording/facts, and avoids a guarantee. **Intentional contrast:** generic instruction-led guidance versus a final coverage determination. The model has not searched a policy and the teaching agent is not an adjudicator; exact wording is nondeterministic.

## Audience questions

- Which part of the response came from the role instructions, and what is still unknown?
- What would have to change before the agent could cite a clause?
- Why start with one simple agent before adding tools and retrieval?

## Troubleshooting and backup evidence

- **Project/model missing:** do not guess a deployment or create Azure resources. Confirm the shared foundation outputs and access with the sandbox owner. Backup: explain the account/project/model diagram on Slides 3–4.
- **Prompt-agent creation or portal labels differ:** confirm current portal experience and role access; portal labels change. Backup: show the instruction file and the optional `verify.ps1` only if a configured agent already exists.
- **Unexpected response or weak guardrail:** rerun the same prompt once, point to the exact instruction that should guide it, and discuss variance. Do not present a single completion as a guarantee. Backup: use the expected-answer style in [demo-runbook.md](demo-runbook.md).

## Security, governance, transition, reset

Use only the synthetic Contoso persona and generic prompts above—never paste a real claim, policyholder identifier, policy wording, or secret. Keep the agent clearly labeled as a training/demo assistant, avoid promises and final decisions, and retain a human review path. The shared foundation is public by design; do not treat it as a production or private-network environment.

**Transition:** Module 02 keeps this agent and introduces Code Interpreter, reusable Skills, and a toolbox; it still does not add policy evidence. For reset, leave the agent in place for the course sequence. If you intentionally created a disposable agent, remove only that asset in the portal; `cleanup.ps1` targets the configured baseline agent and requires explicit confirmation, so do not run it against a shared course agent.

**References:** [Microsoft Foundry overview](https://learn.microsoft.com/azure/foundry/what-is-foundry) · [Agent Service overview](https://learn.microsoft.com/azure/foundry/agents/overview) · [Prompt-agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent)
