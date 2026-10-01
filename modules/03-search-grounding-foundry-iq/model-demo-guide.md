# Module 03 — Instructor model + live demo guide

**Run time:** 13–17 minutes total: a separate 5–7-minute slide-linked context segment, then an 8–10-minute live exemplar.

**Purpose:** repeat one insurance question before and after retrieval is connected, making the shift from plausible instruction-led text to source-backed evidence the central lesson. Use the [demo runbook](demo-runbook.md) for detailed resource setup and optional scripts.

## Outcome and audience promise

Learners see that the same `policy-coverage-advisor` can retrieve from a small synthetic wording corpus and cite clause IDs. They can identify the service, index, Foundry connection, and agent grounding tool in the architecture. Be explicit: retrieval improves traceability; it does not prove the corpus is complete, guarantee retrieval relevance, or delegate final claim authority to the model.

## Readiness and assets

- Required before the live portion: shared foundation, existing `policy-coverage-advisor`, an Azure AI Search service, a populated module index, a Foundry project connection, and the Azure AI Search grounding tool attached. If not already prepared, portal provisioning/indexing is a longer optional setup; do not attempt it inside the 10-minute exemplar.
- Start at `https://ai.azure.com` and select the project. Open the module Search service/index in Azure portal (the index must already contain records).
- The source corpus is [`shared/test-data/policy-wordings.json`](../../shared/test-data/policy-wordings.json), 36 synthetic clause records. Exact exemplar clauses: `HOME-2-3` (escape of water; USD 500 excess) and `HOME-2-4` (trace and access; USD 5,000 limit included within buildings sum insured).
- For setup: Foundry project → **Manage → Project details → Connected resources → Add connection → Azure AI Search**; then open **Agents → `policy-coverage-advisor` → Tools/grounding** and select the connection/index. Portal labels may evolve; use the current Learn article rather than guessing if they differ.
- The optional `infra/search.bicep` creates only a Basic Search service. `src/build_search_index.py` builds/uploads records; `src/connect_search_to_agent.py` handles connection and attachment. Deployment, roles, endpoint/configuration, and optional scripts are pre-work—not actions to run during the short demo.

## Separate slide-linked context segment — 5–7 minutes

Deliver the context **before** entering the live exemplar. This independent segment gives learners the reason for grounding and a clear mental model of what the retrieval path can and cannot establish.

| Context time | Slides | Context to set |
| --- | --- | --- |
| 0:00–1:30 | 1–3 | Establish why fluent insurance language is not evidence. Recall that Modules 01–02 supplied instructions and optional behavior/tooling, not a policy source. |
| 1:30–3:30 | 4–7 | Explain the 36-record synthetic clause corpus, index fields, and source → index → project connection → agent tool → answer flow. Define keyword/vector/hybrid conceptually without claiming this demo generated vectors. |
| 3:30–5:00 | 8–11 | Clarify that “Foundry IQ pattern” is course shorthand for retrieval-backed grounding; the live implementation is direct Azure AI Search. Current Foundry IQ product scope, preview status, supported environments, and labels must be checked in Learn. |
| 5:00–7:00 (optional) | 12–13 | Preview the repeated washing-machine question and expected clause IDs. State the boundary: citations aid inspection but do not establish corpus completeness or final applicability. Transition to Module 04. |

**Bridge into the live demo:** “With that retrieval chain in mind, we'll inspect the already-prepared service and ask the same synthetic question against the connected index.”

## Live exemplar — separate 8–10 minutes, minute by minute

| Live-demo time | Instructor action | Narration and visible evidence |
| --- | --- | --- |
| 0:00–1:00 | Open `policy-coverage-advisor` in the Foundry project; establish that grounding is attached only if already provisioned. | “In Modules 01–02, this agent had instructions and possibly Skills/tools, but no policy source. Fluent text is not evidence.” |
| 1:00–2:00 | Ask the synthetic washing-machine question below before grounding only if an ungrounded baseline version is safely available; otherwise show the prepared baseline transcript. | Point out whether a clause citation is absent. Do not claim every ungrounded answer will hallucinate or produce identical text. |
| 2:00–3:00 | Show the existing Azure AI Search service and the populated `policy-wordings` index/document count. | Explain one JSON record per synthetic clause. The expected corpus has 36 records. Avoid showing keys or credentials. |
| 3:00–4:00 | In Foundry, show **Manage → Project details → Connected resources** and the Search connection; then show the agent's Search grounding configuration. | Evidence is the configured connection/index reference. Do not change connections during the demo; auth and labels vary by environment. |
| 4:00–6:00 | Submit the same washing-machine prompt to the grounded agent. | Look for `HOME-2-3` and `HOME-2-4`, the USD 500 water-loss excess, and USD 5,000 trace-and-access limit (included in, not in addition to, the buildings sum insured). Ask the audience to find these in the local corpus. |
| 6:00–7:00 | Open the two exact clause records from the local JSON file. | Read the source rather than treating the generated summary as contract wording. The local JSON is synthetic teaching data, not a real policy. |
| 7:00–8:00 | Use Slides 8 and 11 for the product terminology and caveat. | The lesson implements direct Azure AI Search grounding. “Foundry IQ pattern” is instructional shorthand; exact managed knowledge-base scope, preview status, supported agent types, and portal labels can change. |
| 8:00–10:00 | Ask the class when a citation is useful and what a retrieved answer still cannot decide; transition to Module 04. | Reinforce that a cited passage can be incomplete or inapplicable to a real schedule/endorsement. Human review remains necessary. |

### Paste-ready synthetic exemplar

```text
A washing machine leak damaged the kitchen floor. Can the policy also cover opening up the building to find the leak source? Use only retrieved synthetic policy wording, cite the relevant clause IDs, state the excess/limit only if the source supports it, and identify what still needs human verification. Do not make a final claim decision.
```

### Exact source evidence for instructor verification

From `HOME-2-3`, the wording says loss/damage to buildings caused by water escaping from washing machines is covered, subject to conditions/exclusions, and an increased USD 500 excess applies. From `HOME-2-4`, following a covered Section 2.3 claim, reasonable removal/replacement costs to find and repair the escape are covered up to USD 5,000 per claim; that limit sits within the buildings sum insured. Avoid implying the entire repair is payable without policy/schedule and facts review.

The index schema has a `content_vector` field. The builder leaves it empty unless a non-placeholder `embeddingDeploymentName` is configured; the module's default text-upload path is not evidence of populated vectors. The tool definition requests vector-semantic-hybrid query type, but do not claim that embeddings were generated or that a particular retrieval mode is visible unless you have verified it in this sandbox.

## Contrast and audience questions

**Intentional contrast:** pre-grounding, uncited instruction-led answer versus the same question with retrieved clause citations. Ask:

- Which exact phrase is evidence, and which is the model's summary?
- What policy schedule or endorsement could change this answer?
- Why does a citation not make this a final coverage determination?

## Troubleshooting and backup evidence

- **No Search service/index or empty count:** this is not a 10-minute repair. Confirm the module service, `searchIndexName`, and identity/roles with the sandbox owner. Backup: open the two synthetic local JSON records and trace source → index → connection → agent on Slide 7.
- **No connection/grounding tool:** check the current project and permitted auth model. Optional `verify.ps1` checks the index and connection/agent reference when configured. Do not paste API keys in chat or repository files. Backup: demonstrate the exact connection path from the runbook using a preconfigured environment screenshot only if it contains no secrets.
- **No citations or wrong clause:** check that the index has current records and the agent references the expected connection/index; rerun once with explicit terms “washing machine,” “escape of water,” and “trace and access.” Backup: compare local `HOME-2-3`/`HOME-2-4` source clauses; do not fabricate citations.
- **Current portal differs:** follow [Learn: connect Azure AI Search to agents](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/ai-search); portal labels and feature scope can change. The module uses direct Search grounding, not a promise of a particular Foundry IQ portal surface.

## Security, governance, transition, reset

Use only the repository's synthetic Contoso clauses and invented scenario; never index or paste customer policy files, claim records, credentials, or regulated data in this classroom demo. Use approved identity-based access where supported; if an environment uses a key-based connection, keep secrets out of this repository and the screen share. Treat retrieval as decision support and inspect source applicability, exclusions, schedule, and human approval needs.

**Transition:** Module 04 moves to code-first hosted agents and delegated specialist orchestration; it does not make the Search corpus a live adjudication authority. For reset, do not alter the shared local corpus or delete an index used by other learners. Remove only a module-owned grounding attachment/connection/service after confirming ownership and downstream use; `cleanup.ps1` detaches, deletes the module connection, and deletes the tagged Search service/index after confirmation.

**References:** [Azure AI Search overview](https://learn.microsoft.com/azure/search/search-what-is-azure-search) · [Connect Search to Foundry agents](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/ai-search) · [Connect Agents to Foundry IQ Knowledge Bases](https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect) · [Foundry runtime components](https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components)
