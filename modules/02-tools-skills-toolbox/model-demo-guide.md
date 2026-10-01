# Module 02 — Instructor model + live demo guide

**Run time:** 13–17 minutes total: separate 5–7-minute slide-linked context, followed by an 8–10-minute live exemplar.

**Purpose:** make the distinction between a model instruction, a callable tool, reusable Skills, and their toolbox packaging visible on the same `policy-coverage-advisor`. This short instructor path complements the detailed [demo runbook](demo-runbook.md); it does not replace it.

## Outcome and audience promise

Learners leave able to name the four layers—agent role, tool capability, Skill behavior, reusable toolbox—and observe one arithmetic example plus one customer-facing rewrite. The agent may calculate and communicate more consistently, but it still does not know a real policy or make an authoritative coverage decision.

## Readiness and assets

- Prerequisite: the shared Foundry foundation and a Module 01 `policy-coverage-advisor` in the project; instructor can edit that agent.
- Open `https://ai.azure.com`, the target project, and the [toolbox definition](src/toolbox.yaml). Keep the five [Skill files](src/skills/) open: `adjudication-rationale`, `claims-tone`, `customer-comms-tone`, `regulatory-disclosure`, and `underwriting-appetite`.
- The portal path is project → **Agents** → `policy-coverage-advisor`; add Code Interpreter in the agent's **Tools** area. The runbook refers to the portal's **Skills experience** and **Toolbox area**. Their exact labels/placement can vary; follow the current portal experience rather than assuming a fixed submenu.
- Live additions are Code Interpreter, the Skills, toolbox, and attachment. The [scripts](deploy.ps1) are optional; File Search and Web Search are conceptual here and not assumed to be provisioned.

## Separate slide-linked context segment — 5–7 minutes

Deliver this framing segment **before** opening the agent configuration. It is in addition to the timed live demo below; use it to establish why capabilities, reusable behavior, and packaging are different things.

| Context time | Slides | Context to set |
| --- | --- | --- |
| 0:00–1:30 | 1–3 | Re-anchor on Module 01's prompt-only `policy-coverage-advisor`. A tool adds an action/capability beyond text generation; distinguish that from simply making the prompt longer. |
| 1:30–3:30 | 4–6 | Contrast Code Interpreter (live arithmetic) with File Search/Web Search (not configured in this demonstration). Introduce Skills as versioned reusable behavior such as tone, disclosure, or decision framing—not evidence sources. |
| 3:30–5:00 | 7–10 | Describe the toolbox as a reusable package of tools and Skills. State the planned live sequence: baseline, calculator, Skills, toolbox, attachment, compare. Make clear portal labels and preview availability can vary. |
| 5:00–7:00 (optional) | 11–14 | Preview calculation and communication examples. Name the boundary: better calculations/wording are not policy grounding or underwriting authority. Preview Module 03's source-backed retrieval. |

**Bridge into the live demo:** “We have separated capability from reusable behavior and packaging; now let's add them to the same agent and see what visibly changes.”

## Live exemplar — separate 8–10 minutes, minute by minute

| Live-demo time | Instructor action | Narration and visible evidence |
| --- | --- | --- |
| 0:00–1:00 | Open the existing `policy-coverage-advisor` in the project; ask the tone prompt below before attaching anything. | “This is the Module 01 baseline: role/instructions, without the capabilities we add today.” Treat the first answer as a comparison sample, not a controlled model benchmark. |
| 1:00–2:00 | In agent configuration → **Tools**, add **Code Interpreter** and save. | Name the operation: this is a calculation-capable tool, not policy retrieval. Tool availability/labels depend on the current portal and project permissions. |
| 2:00–3:00 | Submit the synthetic arithmetic example below. | Check `2,400 − 400 = 2,000`. If the portal exposes tool activity, point to it; do not promise a particular trace panel. Correct text alone does not prove which execution path was used. |
| 3:00–5:00 | Create the five Skills from the matching `src/skills/<name>/SKILL.md` files in the current Skills experience. Use each file's front matter name; save/publish the versions. | Show that each file packages a reusable behavior. Do not paraphrase all five; open `claims-tone` and `regulatory-disclosure` as examples. |
| 5:00–6:00 | In the current Toolbox experience, create `insurance-advisor-toolbox`; include Code Interpreter and the five Skills as in [`src/toolbox.yaml`](src/toolbox.yaml). Save/publish. | A toolbox is a reusable bundle, not a new model. The toolbox definition lists the exact intended membership. |
| 6:00–7:00 | Return to the agent, attach the toolbox, save, then repeat the tone prompt. | Compare readability, empathy, next steps, and the absence of a payment promise. Skills guide behavior; they do not establish coverage facts. |
| 7:00–8:00 | Ask the underwriting referral prompt below, then show Slides 12–14. | The Skill's intended decision vocabulary is ACCEPT / ACCEPT WITH TERMS / REFER / DECLINE; incomplete sprinkler and loss details should favor REFER, not an unsupported final decision. Preview Search grounding next. |
| 8:00–10:00 | If time permits, show the toolbox contents and ask the class what should remain in the core agent prompt. | Close with the governance and setup caveats below. Use the remaining time for questions, not additional unconfigured tools. |

### Paste-ready synthetic prompts

**Calculation (made-up amounts; not a quote or claim payment):**

```text
For a hypothetical assessed claim amount of USD 2,400, apply a USD 400 excess. Show the arithmetic and give a short, provisional explanation. Do not imply that coverage or payment is approved.
```

**Customer communication:**

```text
Rewrite this generic training response for a customer whose car was damaged in a storm: "Coverage may be subject to validation of endorsements and exclusions. Submit documentation." Ask for the next three pieces of information. Do not promise payment or admit liability.
```

**Underwriting framing:**

```text
Training example only: a small commercial property submission has incomplete sprinkler information and one recent water-loss claim. Recommend ACCEPT, ACCEPT WITH TERMS, REFER, or DECLINE; state missing evidence and who must review. Do not invent facts or treat this as a real underwriting decision.
```

### Contrast and evidence

**Intentional contrast:** the baseline prompt-only agent versus the updated behavior/capability bundle. Expected visible evidence is a correctly shown subtraction, a saved toolbox with the five named Skills plus Code Interpreter, and an attached toolbox reference on the agent. The customer rewrite should be empathetic/plain English with clear next steps and no payment promise. Exact answer wording and tool-use UI are not guaranteed. File Search needs files/vector-store/search setup; Web Search needs access and compliance/cost consideration—neither is part of this demo.

## Audience questions

- Which behavior belongs in the agent's role prompt, and which is reusable as a Skill?
- What did Code Interpreter add that a Skill cannot?
- What evidence is still missing before the underwriting example could support a real decision?

## Troubleshooting and backup evidence

- **Agent or Code Interpreter unavailable:** confirm the selected project, edit permission, and current sandbox/tool access. Do not toggle on Web Search or File Search as a workaround. Backup: calculate the same `2,400 − 400` on a whiteboard and show the relevant toolbox YAML.
- **Skill/toolbox UI differs or a Skill cannot be saved:** portal labels and preview availability can vary. Use each `SKILL.md` front matter and [`src/toolbox.yaml`](src/toolbox.yaml) as the source of truth; the optional provisioning path and `verify.ps1` can help only with correctly configured local access.
- **Attached toolbox fails to resolve:** this repository documents a verified-but-version-sensitive `toolbox_reference` incompatibility. Check the toolbox and agent API versions and recreate the reference as described in [known limitations](../../docs/known-limitations.md). Backup: show the five local Skill files and explain the intended bundle without claiming runtime use.
- **Output is overconfident:** rerun with the same synthetic input and point to the human-review/uncertainty language in the Skill; do not use the output as an underwriting decision.

## Security, governance, transition, reset

Keep all inputs synthetic; Code Interpreter operates on user-provided prompts and can produce erroneous calculations, so check arithmetic independently. Skills are behavior guidance, not policy, compliance approval, or model controls. Do not enable public-web/file tools unless their access, cost, and data-handling implications are approved. This Skills/Toolbox experience is documented as preview; verify current Learn guidance.

**Transition:** Module 03 adds a synthetic policy corpus and Azure AI Search grounding. Until then, neither Skills nor this toolbox supplies clause evidence. For reset, preserve the shared Module 01 agent and any reused assets. Detach only this module's toolbox if you created it for the demo. The module cleanup script deletes module-created Skills/toolbox and optionally detaches from the agent; use it only for assets you own, after verifying configuration/ownership and explicit confirmation.

**References:** [Code Interpreter](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/code-interpreter) · [Skills (preview)](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/skills) · [Toolbox overview](https://learn.microsoft.com/azure/foundry/agents/concepts/toolbox-overview) · [Toolbox setup](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/toolbox)
