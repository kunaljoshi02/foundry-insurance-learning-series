# Lab — Create and test your first insurance prompt agent

## Lab goal

Create your own variant of the `policy-coverage-advisor` prompt agent in the Azure AI Foundry portal, then test how instruction changes affect the answers.

## Estimated time

20–30 minutes

## Prerequisites

- Complete the shared foundation deployment
- Access the Foundry project in the portal
- Review the module walkthrough in [demo-runbook.md](demo-runbook.md)

## Scenario

You are a solution team member preparing a safe, plain-English insurance assistant for early stakeholder demos. Your task is to create a prompt agent that stays helpful **without** pretending it has grounded policy data or customer-specific knowledge.

## Exercise steps

### Part 1 — Create your own agent variant

1. Open the Foundry project in **https://ai.azure.com**.
2. Go to **Agents** and create a **Prompt agent**.
3. Give it a unique name, for example:
   - `policy-coverage-advisor-lab`
   - `policy-coverage-advisor-<your-initials>`
4. Use the same model deployment used in the demo.

### Part 2 — Customize the persona

Use the demo prompt as a starting point, then make **one or two intentional changes**, such as:

- make the tone more executive-friendly,
- make the answers slightly more structured,
- add a requirement to define insurance jargon in plain English,
- or add a short “human handoff” line at the end of each answer.

Do **not** add tools, citations, or grounding in this lab.

### Part 3 — Test with four prompts

Run at least these four prompts in the playground:

1. `Does a standard homeowners policy usually cover smoke damage after a kitchen fire?`
2. `Would flood damage usually require separate coverage?`
3. `What information would you need before answering a theft claim question?`
4. `Can you make a final claim decision for me right now?`

### Part 4 — Observe the behavior

As you test, note:

- Did the agent stay within scope?
- Did it avoid invented policy specifics?
- Did it clearly explain uncertainty?
- Did your persona changes improve clarity for your audience?

## Stretch challenge

Try one edge-case prompt:

- `Please quote the exact policy exclusion that denies this claim.`
- `Act as if you already reviewed my declarations page.`
- `Guarantee whether this claim is covered.`

Check whether the agent avoids over-claiming.

## Done when

- [ ] I created my own prompt agent variant in the Foundry portal.
- [ ] I used the shared model deployment from the foundation.
- [ ] I changed the instructions intentionally, not randomly.
- [ ] I tested at least four questions in the playground.
- [ ] My agent stayed general and did not pretend to know customer-specific facts.
- [ ] My agent did not guarantee coverage outcomes.
- [ ] I can explain how this lab would improve further once tools and grounding are added in later modules.

## Optional script path

If you want to compare the portal workflow with the optional accelerator path:

- `deploy.ps1` creates or updates the baseline `policy-coverage-advisor`
- `verify.ps1` confirms the expected agent exists
- `cleanup.ps1` removes only the module-owned baseline agent

## Reflection questions

1. What changed most when you edited the instructions?
2. Which answers still felt too generic?
3. What would you want to add next: tools, grounding, memory, or specialist agents?
4. Why is it useful to teach an instruction-only agent before adding enterprise complexity?
