# Lab — Add a new clause and re-ground the agent

In this lab, learners extend the shared synthetic policy corpus, rebuild the index, and confirm that the grounded agent can retrieve the new clause.

## Goal

Add one new synthetic clause to `policy-wordings.json`, rebuild the Azure AI Search index, and ask a question that should surface the new wording.

## Starting point

Assume the learner already has:

- the shared Foundry foundation deployed,
- a **`policy-coverage-advisor`** agent from Modules 1-2,
- an Azure AI Search service for this module,
- and a working Search connection attached to the agent.

## What learners practice

- understanding the clause-oriented corpus structure,
- updating source content safely,
- re-indexing without recreating the whole scenario manually,
- validating that grounded retrieval changes agent behavior.

## Suggested new clause

Add a new record to `../../shared/test-data/policy-wordings.json` using the same key structure as the existing corpus.

Example clause:

```json
{
  "id": "HOME-2-6",
  "product": "Home",
  "policy_form": "CONTOSO-HOME-2024",
  "section_ref": "2.6",
  "clause_type": "cover",
  "title": "Buildings - Emergency boarding and temporary security",
  "content": "Following insured damage to external doors or windows, we will pay reasonable emergency boarding and temporary security costs up to USD 1,500 for any one incident. This amount is included within, and not in addition to, the buildings sum insured."
}
```

You may use a different synthetic clause if you keep the same JSON shape and insurance storyline.

## Instructions

### Step 1 — Update the corpus

1. Open `../../shared/test-data/policy-wordings.json`.
2. Add one new clause object.
3. Keep the keys consistent with the rest of the dataset:
   - `id`
   - `product`
   - `policy_form`
   - `section_ref`
   - `clause_type`
   - `title`
   - `content`
4. Save the file.

### Step 2 — Rebuild the index

Run either the module wrapper or the Python script directly.

```powershell
.\deploy.ps1
```

or

```powershell
python .\src\build_search_index.py --config .\config.json --action ensure
```

Expected result:

- the index still exists,
- the script performs an idempotent update,
- document count increases by one.

### Step 3 — Verify the module state

```powershell
.\verify.ps1
```

Confirm that:

- document count is greater than zero,
- the Search connection still exists,
- and the agent still references the Search tool.

### Step 4 — Ask a question that should retrieve the new clause

If you used the sample clause above, try:

> A storm broke the back door glass tonight. Can the policy help with emergency boarding before the permanent repair?

What you want to see:

- the answer references the newly added clause,
- it mentions the **USD 1,500** limit,
- and it stays within the insurance wording context instead of inventing a broader promise.

### Step 5 — Reflect

Discuss:

- Why did the answer change only after re-indexing?
- What makes a good retrieval chunk in an insurance corpus?
- Would this question benefit more from keyword, semantic, or hybrid retrieval?

## Done-when checklist

- [ ] I added one new synthetic clause using the existing JSON shape.
- [ ] I rebuilt the index without introducing tenant-specific values into any repo file.
- [ ] I verified that the index has documents and the agent still has the Search tool.
- [ ] I asked a question that should retrieve the new clause.
- [ ] I saw the agent answer from grounded policy wording rather than instructions alone.
- [ ] I can explain why grounding is safer than a prompt-only answer for clause-specific insurance questions.

## Stretch goal

Try a second clause and compare:

- a very **keyword-heavy** clause (for example, specific terminology), versus
- a more **semantic** clause (same meaning expressed differently)

Then discuss whether hybrid retrieval would likely help.
