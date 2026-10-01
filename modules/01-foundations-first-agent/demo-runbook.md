# Demo runbook — Foundations + first prompt agent

This runbook is written for an instructor or facilitator delivering Session 1 in a **portal-first** format. The optional scripts are accelerators only.

## Demo goals

By the end of the demo, learners should see:

1. the deployed Foundry foundation,
2. the relationship between project and model deployment,
3. a working prompt agent named `policy-coverage-advisor`,
4. and a few sample playground interactions.

## Before you start

- Complete the shared foundation deployment described in [`../../foundation/README.md`](../../foundation/README.md).
- Copy `config.example.json` to `config.json` only if you plan to use the optional scripts.
- Sign in to the Azure AI Foundry portal with an identity that can use the project.

---

## Part A — Verify the foundation in the portal

### A1. Open the Foundry portal

1. Browse to **https://ai.azure.com**.
2. Sign in with your sandbox identity.
3. Open the Foundry project created by the foundation deployment.

### A2. Confirm the expected project-level assets

From the project home page, verify:

- the **project name** matches the foundation output `foundryProjectName`,
- the **project endpoint** is available and matches the format `<your-foundry-endpoint>`,
- and the **chat model deployment** from `chatModelDeploymentName` appears under deployed models.

### A3. Explain the architecture while learners are looking at the portal

Talking points:

- The **Foundry account** is the Azure resource boundary.
- The **project** is the working surface for prompts, agents, evaluations, and tools.
- The **model deployment** is the named model the agent will use.
- The **playground** is where we safely validate behavior before building anything more advanced.

---

## Part B — Create the first prompt agent in the portal

### B1. Start a new prompt agent

1. In the project, go to **Agents**.
2. Choose **Create agent**.
3. Select **Prompt agent**.

### B2. Enter the basic agent details

Use these values:

- **Name:** `policy-coverage-advisor`
- **Description:** `Instruction-only insurance coverage advisor for Session 1 of the curriculum.`
- **Model:** use the deployed chat model from the foundation, such as `<your-chat-model-deployment-name>`

### B3. Paste these instructions

Use the full prompt below:

> You are Policy Coverage Advisor for Contoso Insurance, a calm and concise assistant used for training and demonstration.
>
> Your job is to answer general insurance coverage questions in plain English using only the information in the conversation and these instructions. Do not claim to have reviewed a real policy document, declarations page, endorsement, claim file, or customer record unless the user explicitly provides that information in the chat.
>
> When answering a coverage question, use this structure:
> 1. Short answer
> 2. Why it might be covered or not covered
> 3. What information is still needed
> 4. Recommended next step
>
> Important guardrails:
> - Never guarantee that a claim will be paid.
> - Never invent policy clause numbers, limits, deductibles, endorsements, waiting periods, or exclusions.
> - Do not pretend to use external tools, web search, or policy grounding.
> - If the user asks for a final claim decision, legal advice, regulatory certainty, or customer-specific adjudication, say that a licensed insurance professional or claims handler must confirm.
> - Keep the tone professional, empathetic, and easy for both business and technical audiences to follow.
>
> You may provide general examples, but label them clearly as examples rather than confirmed policy terms.

### B4. Save the agent

1. Review the summary.
2. Create or save the prompt agent.
3. Open the agent playground.

---

## Part C — Test the agent in the playground

### C1. Sample question 1

**Prompt**

`Does a standard homeowners policy usually cover damage from a kitchen fire?`

**Expected answer style**

- starts with a short answer such as “Often yes, but it depends”
- explains why accidental fire is commonly covered in principle
- notes missing facts such as cause, exclusions, occupancy, or policy wording
- ends with a human-review next step

### C2. Sample question 2

**Prompt**

`Would flood damage normally be included in the same policy?`

**Expected answer style**

- clearly says flood is often separate or endorsement-dependent
- avoids pretending to know the customer’s actual coverage
- suggests checking the declarations or endorsements

### C3. Sample question 3

**Prompt**

`What details would you need before answering a stolen bicycle claim question?`

**Expected answer style**

- produces a useful checklist
- mentions ownership, location, proof of loss, policy type, deductible, and endorsements
- stays educational and practical

### C4. Sample question 4

**Prompt**

`Can you confirm this claim will definitely be paid?`

**Expected answer style**

- refuses certainty
- explains that final determination requires policy review and human handling
- maintains a calm, professional tone

### C5. Optional follow-up prompts

- `How would your answer change if the property was vacant for 90 days?`
- `How should I explain a deductible to a policyholder in plain English?`
- `What is the difference between general guidance and an actual coverage determination?`

---

## Part D — Teaching notes

Use this moment to make the curriculum arc explicit:

- **Today:** instructions + model + playground
- **Module 2:** tools and toolbox
- **Module 3:** grounding with policy content
- **Module 4:** specialist agents and orchestration
- **Modules 5–8:** memory, identity, observability, and enterprise networking

Frame Session 1 as the “smallest useful agent” that makes later complexity easier to understand.

---

## Part E — Optional script path

These scripts are optional accelerators and do **not** replace the portal walkthrough:

```powershell
# 1. Copy the example config and fill in your values.
Copy-Item .\config.example.json .\config.json

# 2. Preview what would happen.
.\deploy.ps1 -WhatIf

# 3. Create or update the prompt agent.
.\deploy.ps1

# 4. Verify the agent exists.
.\verify.ps1
```

Cleanup after the session:

```powershell
.\cleanup.ps1
```

## Demo close

End by restating:

- what Foundry is,
- why a prompt agent is a useful first milestone,
- and what gets added next when tools and grounding arrive in Modules 2 and 3.
