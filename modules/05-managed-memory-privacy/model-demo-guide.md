# Module 05 — Instructor model demo: managed Memory and privacy

**Performance length:** 6-minute slide context + 8-minute live exemplar · **Slides:** [slides 1–14](slides.md) · **Mode:** portal-first, with a prepared-agent fallback

## Outcome and audience promise

Show that the existing `policy-coverage-advisor` can carry a low-risk formatting preference from one conversation into a new conversation for the same signed-in identity, then make the privacy boundary visible. The audience should leave understanding that personalization is not permission to persist claim facts, and that recall is a preview capability whose current behavior must be checked against Microsoft Learn.

This is suitable for mixed insurance and developer audiences: business participants see the user experience and erasure principle; developers can inspect the `memory_search_preview` attachment and user-scope configuration.

## Readiness and staging

- **Pre-stage:** a public shared Foundry project, the existing `policy-coverage-advisor`, and (if doing live recall) a managed Memory store attached to the agent's prepared version. Sign in as a training identity that can use the project.
- **Optional setup, not a live-demo step:** create/attach a Memory store or update an agent version. The portal flow and exact labels can vary in this preview. Use the module's [demo runbook](demo-runbook.md) or [Memory Learn article](https://learn.microsoft.com/azure/foundry/agents/how-to/memory-usage) to prepare it before class; do not imply that a menu or setting is present in every tenant.
- **Verified readiness boundary:** the repository's reference pattern requires a public project; managed Memory is not supported in VNet-injected projects in the verified behavior described in [known limitations](../../docs/known-limitations.md#3-managed-memory-preview-networking-and-identity-scope-module-5).
- **Keep synthetic:** no names, live claim numbers, addresses, health details, financial information, credentials, or other real customer data.
- **Have ready:** a second browser conversation in the same account is not required; you must start a genuinely new conversation, not continue the first thread.

## Exact navigation and assets

1. Open `https://ai.azure.com`, select the shared project, then **Agents → `policy-coverage-advisor` → playground/chat**. If your portal labels differ, stop at the agent and use the current Learn article rather than guessing at a Memory setting.
2. If checking configuration, open the agent's configuration/tools area and verify the prepared Memory attachment. If the portal exposes the Memory store/scope management view, use it only for the current demo identity and only to show that preference data exists; do not expand unrelated records.
3. Local reference assets: [`docs/privacy-notes.md`](docs/privacy-notes.md) (safe-data boundary), [`src/provision_memory.py`](src/provision_memory.py) (scope `{{$userId}}`; setup/cleanup helper, not a portal guarantee), [`src/privacy_tools.py`](src/privacy_tools.py) (targeted scope listing/purge helpers), and [`verify.ps1`](verify.ps1) (configuration check only; does not read memory contents).

## Context setting — 6 minutes, separate from the live demo

Use this short framing segment before the hands-on performance. It is not counted in the 8-minute live exemplar below.

| Time | Slides | Context beat |
| --- | --- | --- |
| 0:00–2:00 | [1–4](slides.md) | Place Memory in the eight-session story. Explain the distinction between thread history and durable preference recall. Read the three safe examples and contrast them with real claim/customer data, which this lesson will not persist. |
| 2:00–4:00 | [5–7](slides.md) | Establish the privacy model: signed-in identity scope, not a shared team notepad. Walk through the architecture and ask who should be able to see a stored preference. Describe inspection and erasure as governance questions, not a promise that every tenant exposes the same portal controls. |
| 4:00–6:00 | [8, 12–14](slides.md) | Preview the demonstration: prepared agent, new conversation, same-user recall, then targeted privacy discussion. State the verified public-project preview boundary, direct learners to current Learn docs for changing behavior, and tee up identity and OBO as the next session's focus. |

## Minute-by-minute live exemplar

| Time | Slide(s) | Instructor action and narration |
| --- | --- | --- |
| 0:00–1:00 | [1–6](slides.md) | Frame the promise: “We are extending the same advisor, not creating a new one. We will remember answer style, not customer facts.” Contrast thread history with durable memory. |
| 1:00–2:00 | [7–8](slides.md) | Navigate to the prepared agent. Point out the existing agent identity and, if visible, its Memory attachment. Say explicitly whether the store was pre-provisioned; do not create a resource during the exemplar. |
| 2:00–3:00 | [9](slides.md) | In conversation A, paste the preference below. Explain why it is low-risk and user-owned. If tool activity is exposed, show only the Memory activity indicator, not stored contents. |
| 3:00–5:00 | [10](slides.md) | Start a new conversation as the same signed-in user and ask the second prompt. Let the learner observe formatting before explaining it. Point out that the prompt requests policy evidence and forbids invented coverage conclusions. |
| 5:00–6:00 | [11–12](slides.md) | State the identity-scope boundary and public-project preview limitation. If targeted scope controls are available in this tenant, show only that this user's preference scope is addressable; otherwise describe the control and do not improvise a delete path. |
| 6:00–7:00 | [11](slides.md) | If a prepared, disposable demo identity/store and known targeted clear path are available, clear only the current user's scope and start another new conversation to test. Otherwise skip the destructive action and use the backup evidence below. |
| 7:00–8:00 | [13–14](slides.md) | Close with the boundary: memory personalizes format; it does not supply policy evidence or authorize a decision. Transition to Module 06: who the caller is and what the agent may do as that identity. |

## Copy/paste synthetic inputs

**Conversation A — store a preference**

```text
Remember that I prefer synthetic settlement summaries in bullet points, with the likely outcome first, and no more than five bullets. This is only a response-format preference; do not store claim or customer details.
```

**Conversation B — new thread, same signed-in user**

```text
For a synthetic training example only: a storm damaged a detached garage. Summarize what the policy wording available to you says. Put the likely position first, use no more than five bullets if you remember my preference, cite the relevant clause if one is available, and say when the wording is insufficient. Do not infer coverage or invent a clause.
```

## Expected visible evidence and narration

- Conversation A acknowledges a preference, or exposes memory-tool activity if the UI makes that available. Do not promise a specific acknowledgement string or tool trace.
- Conversation B is a new conversation under the same signed-in identity. The visible evidence is its formatting (bullet points, likely position first, concise length), not a guaranteed coverage outcome.
- Narrate: “The result we are testing is cross-conversation preference recall. Any coverage statement still needs policy wording and a citation.”
- If targeted deletion is available and used on a disposable setup, a later conversation should no longer consistently apply the erased preference. Recall timing and exact phrasing are not deterministic; absence on one response alone is not conclusive proof of erasure.

## Intentional contrast and boundary

**Contrast:** preference memory is not thread history, shared team knowledge, or a source of policy truth. A same-user preference may shape presentation; it must not override grounding, safety instructions, or coverage evidence. The verified reference configuration uses the signed-in user's scope (`{{$userId}}`), not a shared team bucket.

**Boundary:** managed Memory is preview, and the validated course pattern is for a public project. No claim is made here that private/VNet-injected projects are supported or that another user's data can be inspected. See [Microsoft Learn: Memory usage](https://learn.microsoft.com/azure/foundry/agents/how-to/memory-usage) and [What is Memory?](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory).

## Audience questions

- What belongs in durable memory, and what belongs in the policy source?
- What evidence proves this is a new conversation for the same user?
- How would you verify and erase one user's preference without inspecting another user's data?
- What should the agent do if memory suggests a style but policy evidence is missing?

## Troubleshooting and backup evidence

- **No preference in the second response:** confirm it is a new conversation under the same signed-in account; confirm the Memory store is attached to the agent version being used; allow for preview update delay. Do not repeatedly add the preference as that muddies the demonstration.
- **Memory controls are absent or renamed:** do not claim a particular portal path works in every tenant. Use the current Learn article and switch to configuration evidence from the pre-staged agent.
- **No memory tool trace or inconsistent formatting:** report that honestly. Show `python .\src\provision_memory.py --action verify --config .\config.json` only if an instructor-prepared config exists; it verifies store/attachment and `{{$userId}}` scope, not recall or memory contents. The README's success criteria and this module's scope helper are supporting configuration evidence, not a substitute for live recall.
- **Fallback:** use a pre-staged same-user before/after capture labeled as prepared evidence, then explain the targeted-erasure principle. Never present a screenshot as a live run.

## Security, governance, and reset

Keep prompts synthetic. Avoid displaying user identifiers or unrelated memory records; do not log raw preference text. Erasure must target the current demo identity only. For reset, use the portal's targeted clear control only if its target is unambiguous and the store is disposable. Otherwise leave the prepared store intact. The optional `cleanup.ps1` / provisioning helper can detach and delete the module store; targeted purge is followed by store cleanup in that helper, so **do not run it as a casual demo reset**. No deployment or resource mutation is part of this exemplar.

## Transition

“Module 05 showed how to remember responsibly. Module 06 asks who is calling, which identity a tool sees, and when a delegated user token is required.”
