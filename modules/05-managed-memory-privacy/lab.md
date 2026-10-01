# Lab — Managed Memory + privacy check

## Lab goal

Extend the existing `policy-coverage-advisor` so it remembers a few **safe, synthetic** user
preferences across conversations, then perform a privacy check by clearing that memory and proving
it is gone.

## Estimated time

25–35 minutes

## Prerequisites

- The shared public foundation project exists.
- `policy-coverage-advisor` already exists from the earlier modules.
- You can open the project in the Foundry portal.
- You have reviewed [demo-runbook.md](demo-runbook.md).

## Safety rule for this lab

Use **synthetic training data only**.

Do **not** store:

- real customer names
- claim numbers from live systems
- home addresses
- payment details
- medical details
- anything that would count as real PII or confidential claim content

## Scenario

You are preparing the insurance advisor for repeat interactions with a claims handler who prefers a
consistent answer style. You want the agent to remember the handler's presentation preferences
across conversations while preserving user-level privacy boundaries.

## Exercise steps

### Part 1 — Attach or enable Memory

1. Open **https://ai.azure.com**.
2. Open your project.
3. Open **`policy-coverage-advisor`**.
4. Enable or attach a managed Memory store for the agent.
5. Keep the scope aligned to **per signed-in user** behavior.

### Part 2 — Store 2–3 preferences

In the first conversation, explicitly store preferences like these:

1. `Remember that I prefer settlement summaries in bullet points.`
2. `Remember that I want the likely coverage outcome first.`
3. `Remember that I want no more than five bullets.`

Write down exactly what you told the agent to remember.

### Part 3 — Start a new conversation

Open a **new conversation** and ask a fresh question such as:

> A customer reports storm damage to a detached garage. Summarize the likely coverage position.

Record what the agent recalls automatically.

### Part 4 — Test the scope boundary

Record which things were recalled and which were **not**. Consider:

- Was the output in bullet points?
- Was the likely outcome listed first?
- Did the response stay concise?
- Did the agent invent anything you never asked it to remember?

If you have access to a second safe test identity, optionally repeat the same question there and
note whether the preferences are absent until explicitly stored for that user.

### Part 5 — Privacy check: clear the memory

1. Go to the Memory store / Memory management experience.
2. Find the scope or memory records for **your own** signed-in identity.
3. Clear the remembered preference data for that identity only.
4. Start another new conversation and ask the same or a similar question.

Observe whether the earlier preferences are now gone.

## Worksheet prompts

Write brief notes for each:

1. Which preferences were recalled in a later conversation?
2. Which preferences were **not** recalled?
3. What would be risky to store here in a real insurance workflow?
4. Why is user-scoped erasure important?

## Done-when checklist

- [ ] I attached or enabled a managed Memory store on the agent.
- [ ] I stored at least **two** explicit preferences.
- [ ] I started a **new** conversation and observed what the agent recalled.
- [ ] I wrote down what was recalled versus what was not.
- [ ] I performed a privacy check by clearing my stored memory.
- [ ] I confirmed the earlier preference was no longer recalled after the clear action.
- [ ] I can explain why real PII should not be used in this curriculum's memory demos.

## Stretch goal

Try one preference that the agent **should not** over-personalize, such as:

> Remember that I prefer a quick answer.

Then see whether the agent still preserves necessary safety language and uncertainty handling. The
goal is to show that memory should personalize **format**, not bypass guardrails.

## Reflection

1. When is managed Memory the right tool versus a grounded document source?
2. What is the difference between deleting a store and clearing one user's scope?
3. How does this privacy lesson prepare you for Module 6 on identity, RBAC, and OBO?
