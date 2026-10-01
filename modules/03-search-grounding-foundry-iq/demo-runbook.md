# Demo runbook — Session 3

This runbook adds **Azure AI Search grounding** to the existing **`policy-coverage-advisor`** from Modules 1-2.

Use the **portal path first** for teaching. Use the script path only as an accelerator.

## Demo outcome

By the end of the demo, learners should see that:

- the policy corpus is indexed in Azure AI Search,
- the Foundry project has a Search connection,
- the agent now uses Search as a grounding source,
- and answers include clause-aware evidence instead of prompt-only reasoning.

## Before you start

- The shared foundation from `../../foundation/` already exists in your sandbox.
- A prompt agent named **`policy-coverage-advisor`** exists from Module 1.
- If you completed Module 2, the same agent may already have Skills/toolbox attachments.
- You have the local module files available.
- You are prepared to explain any preview caveats by linking to Learn rather than asserting undocumented current-state behavior.

## Part 1 — Baseline the pre-grounded behavior

1. Open Microsoft Foundry and open your project.
2. Open **`policy-coverage-advisor`**.
3. In the playground, ask a clause-sensitive question such as:

   > A washing machine leak damaged the kitchen floor. Can the policy pay to open up the building to find the source of the leak?

4. Call out the risk:
   - the answer may sound reasonable,
   - but it is still relying on prompt instructions unless grounded content is attached,
   - and it may not cite the exact clause basis.

## Part 2 — Create or confirm the Azure AI Search service

### Portal path

1. Open the Azure portal.
2. Create a new **Azure AI Search** resource if you do not already have one for this module.
3. Use **Basic** tier for the course lab.
4. Apply tags so cleanup can identify course-owned resources:
   - `course = foundry-insurance-learning-series`
   - `module = 03-search-grounding-foundry-iq`
5. Wait for deployment to finish.

### Optional script path

```powershell
Copy-Item .\config.example.json .\config.json
# Edit config.json first.

.\deploy.ps1 -WhatIf
.\deploy.ps1
```

## Part 3 — Build the search index from the shared corpus

### Why this matters

Learners should see that grounding starts with **retrieval-ready source content**, not just attaching a tool checkbox.

### Dataset

The module uses the shared synthetic dataset:

- `../../shared/test-data/policy-wordings.json`

It already contains 36 clause-shaped records across Home, Motor, and Liability.

### Portal explanation

Explain the index design in plain language:

- searchable text fields: `title`, `content`
- structured filter fields: `product`, `policy_form`, `section_ref`, `clause_type`
- optional vector field placeholder: `content_vector`

### Optional script path

```powershell
python .\src\build_search_index.py --config .\config.json --action ensure
```

Expected outcome:

- the index exists,
- documents are uploaded,
- verification shows a document count greater than zero.

## Part 4 — Add the Search connection in Foundry

### Portal path

1. In Microsoft Foundry, open your project.
2. Go to **Manage** > **Project details** > **Connected resources**.
3. Select **Add connection**.
4. Choose **Azure AI Search**.
5. Browse to the Search service you created for this module.
6. Choose the authentication model supported in your sandbox.
   - If you use Microsoft Entra ID / managed identity, make sure the Foundry identity has the required Search roles.
   - If your environment still uses key-based setup, explain that the portal can guide you through it, but do not commit keys into any file in this repo.
7. Save the connection.

### Teaching note

This module prefers **direct Search connection + agent grounding tool**. It does **not** cover the APIM path from Module 8.

## Part 5 — Attach Azure AI Search to the agent

### Portal path

1. Open **`policy-coverage-advisor`** in Foundry.
2. Open the **Tools** or grounding configuration area for the agent.
3. Add **Azure AI Search**.
4. Select the project connection you created.
5. Select the index named in your module config.
6. Save the change.
7. If the portal exposes query mode options, explain the difference between:
   - simple / keyword
   - vector
   - semantic
   - hybrid

### Optional script path

```powershell
python .\src\connect_search_to_agent.py --config .\config.json --action ensure
```

## Part 6 — Show grounded Q&A with clause citations

### Demo prompt A — escape of water + trace and access

> A washing machine leak damaged the kitchen floor. Can the policy also cover opening up the building to find the leak source?

Expected grounded answer pattern:

- cites **`HOME-2-3`** for escape of water
- cites **`HOME-2-4`** for trace and access
- mentions the **USD 5,000** trace-and-access limit
- mentions the higher **USD 500** water-loss excess

### Demo prompt B — delivery driving exclusion

> The insured was delivering food for an app when the crash happened. Is own-damage cover still available?

Expected grounded answer pattern:

- cites **`MOTOR-1-1`** for excluded use classes
- cites **`MOTOR-5-1`** for hire-or-reward exclusion
- distinguishes own-damage cover from minimum statutory third-party obligations

### Demo prompt C — wet floor liability

> A customer slipped on a wet floor with no warning sign. Which clauses matter most?

Expected grounded answer pattern:

- cites **`LIAB-2-3`** for occupiers duty / inspection regime
- cites **`LIAB-6-2`** for wet-floor signage and cleaning log condition precedent

## Part 7 — Explain the “Foundry IQ” pattern

Use a conceptual explanation, not a product-marketing claim:

- the runtime retrieves relevant passages,
- grounds the model on those passages,
- and returns an answer that can cite sources.

Safe phrasing:

> In this course, we use “Foundry IQ pattern” as shorthand for retrieval-backed grounding in Foundry Agent Service. Exact portal labels, managed knowledge-base experiences, and preview scope can change, so we follow current Learn docs instead of memorizing point-in-time UI text.

## Part 8 — Debrief

Ask learners:

- What changed between prompt-only and grounded behavior?
- Why is a clause citation more trustworthy than a fluent answer with no source?
- When would keyword search be enough, and when would hybrid/vector retrieval help more?

## Read-only verification

```powershell
.\verify.ps1
```

Expected checks:

- Search index exists and document count is greater than zero
- Foundry connection exists
- `policy-coverage-advisor` references the Search tool
