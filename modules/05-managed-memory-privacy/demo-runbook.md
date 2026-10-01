# Demo runbook — Managed Memory + user scope/privacy

This runbook extends the existing **`policy-coverage-advisor`** prompt agent with managed Memory.
The demo is intentionally **portal-first**. The scripts in this module are optional accelerators.

## Demo outcome

By the end of the demo, learners should see that:

1. a user can store a low-risk preference in one conversation,
2. the same user can get that preference recalled in a new conversation,
3. a different user should not inherit it automatically,
4. and memory can be inspected or cleared for one user as a privacy control.

## Before you start

- The shared public foundation project is already deployed.
- The prompt agent **`policy-coverage-advisor`** already exists from earlier modules.
- You are signed in with a training identity that can edit prompt agents in the project.
- You are using **synthetic**, low-risk preference text only.

> [!WARNING]
> Managed Memory is still a **preview** feature. The validated reference behavior for this
> curriculum used a **public project** for the Memory demo. If the portal or networking behavior
> differs in your tenant, re-check the current Microsoft Learn Memory docs before presenting the
> feature as generally available.

---

## Part A — Baseline the existing agent

1. Open **https://ai.azure.com**.
2. Open your shared Foundry project.
3. Go to **Agents** and open **`policy-coverage-advisor`**.
4. In the playground, ask a baseline question such as:

   > A customer reports hail damage to a roof. Summarize the likely coverage position.

5. Point out that the answer might be useful, but the agent is not yet remembering any personal
   formatting preferences across conversations.

---

## Part B — Enable managed Memory on the agent

If the portal wording changes, use the current Microsoft Learn Memory article as your click-path
reference.

### B1. Create or select a Memory store

1. In the agent configuration, open the **Memory** or **Tools** area.
2. Choose to create or attach a **managed Memory store**.
3. Use a name such as `policy-coverage-advisor-memory`.
4. Keep the scope pattern aligned to **per signed-in user** behavior.
5. Use an embedding model already deployed in the project, such as
   `text-embedding-3-small`, if the portal asks for it.

### B2. Review the memory settings

Use settings that align with the training goal:

- **User profile memory:** enabled
- **Chat summary memory:** enabled
- **Procedural memory:** enabled if available in the current preview
- **Retention / TTL:** leave at the preview default unless your demo requires a different setting

### B3. Save the updated agent

1. Save or publish the updated configuration.
2. Return to the agent playground.

---

## Part C — Conversation 1: store a preference

Use an intentionally safe preference:

> Remember that I prefer settlement summaries in bullet points, with the likely outcome first, and no more than five bullets.

### What to point out

- The user explicitly asked to remember something.
- The information is a **formatting preference**, not real customer data.
- The agent should confirm the remembered preference without inventing extra details.

If your environment surfaces tool traces or memory activity, briefly show that the Memory tool was
used.

---

## Part D — Conversation 2: prove recall in a new conversation

Start a **new conversation** with the same signed-in user.

Ask:

> A customer reports smoke damage after a kitchen fire. Summarize the likely coverage position.

### Expected outcome

The response should reflect the earlier preference, for example:

- bullet-point structure
- likely outcome first
- concise format

### Explain the learning point

This is not just thread continuity. It is **cross-conversation recall** for the same identity.

---

## Part E — Scope boundary discussion

Explain what should happen for another signed-in user:

- they can have their **own** preferences,
- but they should **not** automatically inherit this user's stored preferences.

If you have a safe secondary demo identity available, repeat the same question under that user and
observe whether the formatting preference is absent until that user stores their own preference.

If you do **not** have a second identity available, explain the model verbally and keep the demo to
the single-user recall plus the privacy controls in Part F.

---

## Part F — Privacy controls: inspect and clear one user's memory

The goal is to show **targeted** privacy handling, not bulk deletion.

### F1. Inspect the memory scope

From the Memory store experience in the portal, or the relevant admin view if exposed:

1. Open the Memory store attached to the agent.
2. Find the stored scope that corresponds to the current signed-in user.
3. Show only the minimum safe details needed for the demo:
   - that a per-user scope exists
   - that the store holds remembered preference data for that scope

Do **not** expand into unrelated or sensitive content.

### F2. Clear the remembered preference

Use the portal's delete / clear action for the selected user scope or memory record, if available.

If the portal preview instead exposes this through a store-management flow, follow that targeted
delete path and narrate the privacy principle:

- erase **this user's** memory,
- not everyone else's,
- and not the entire project unless teardown is intentional.

### F3. Prove the memory is gone

Start another new conversation and ask:

> Summarize the likely coverage position for a detached garage fire.

Expected result:

- the answer should no longer consistently honor the earlier bullet-point preference,
- or it should reflect only whatever remains after the targeted erase.

That closes the privacy loop.

---

## Optional script path

If you want a repeatable accelerator instead of configuring everything manually:

```powershell
Copy-Item .\config.example.json .\config.json
# Edit config.json with your own placeholders.

.\deploy.ps1 -WhatIf
.\deploy.ps1
.\verify.ps1
```

Optional targeted purge during teardown:

```powershell
.\cleanup.ps1 -PurgeUserData -UserIdentity "<user-scope-or-identity>"
```

> `verify.ps1` only checks store + attachment configuration. It does **not** dump user memory
> contents.

## Debrief questions

1. What kinds of information belong in memory versus grounding data sources?
2. Why is per-user scope critical for privacy?
3. What is the operational difference between deleting a whole store and erasing one user's scope?
4. Why should preview networking limitations be called out explicitly in customer-facing training?
