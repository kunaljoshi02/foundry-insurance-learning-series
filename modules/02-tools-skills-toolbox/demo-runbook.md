# Demo runbook

This runbook extends the earlier **policy-coverage-advisor** agent with a toolbox that contains:

- **Code Interpreter**
- **adjudication-rationale**
- **claims-tone**
- **customer-comms-tone**
- **regulatory-disclosure**
- **underwriting-appetite**

Use the portal path first. Use the script path only if you want a faster, repeatable demo.

## Demo outcome

By the end of the demo, learners should see that:

- the same agent can now do simple calculations
- responses become more consistent and reusable
- the reusable unit is now a **toolbox**, not just a long prompt

## Before you start

- A Foundry project exists from the shared foundation.
- A prompt agent named `policy-coverage-advisor` already exists from Module 1, or an equivalent
  agent has been created in your sandbox.
- You have the local files in this module folder available.
- If you use web search or file search in discussion, present them conceptually unless the
  required setup already exists in your sandbox.

## Portal path

### Part 1 - Baseline the agent

1. Open Azure AI Foundry.
2. Open your project.
3. Open the existing **policy-coverage-advisor** agent.
4. In the playground, run a simple prompt such as:

   > A customer had a kitchen water leak. Explain whether accidental escape of water might be
   > covered and what information we still need.

5. Call out that the answer is prompt-only: it may be correct, but tone, disclosure, and decision
   framing are embedded directly in the agent instructions.

### Part 2 - Add Code Interpreter

1. In the agent configuration, open the **Tools** area.
2. Add **Code Interpreter**.
3. Save the change.
4. Run a calculation prompt:

   > For a covered loss of 1,250 with a 250 excess and 10% depreciation applied before the excess,
   > show the net payable and explain the math step by step.

5. Expected richer behavior:
   - the agent can calculate reliably
   - the response can show the arithmetic cleanly
   - the agent is no longer relying only on natural-language estimation

### Part 3 - Create the Skills

Create five Skills from the files under `src/skills/`:

- `adjudication-rationale\SKILL.md`
- `claims-tone\SKILL.md`
- `customer-comms-tone\SKILL.md`
- `regulatory-disclosure\SKILL.md`
- `underwriting-appetite\SKILL.md`

For each Skill:

1. Open the Skills experience in the portal.
2. Create a new Skill.
3. Use the Skill name from the file's front matter.
4. Paste or upload the `SKILL.md` content.
5. Publish or save the version.

### Part 4 - Create the toolbox

1. Open the Toolbox area in the portal.
2. Create a new toolbox named for this module.
3. Add:
   - Code Interpreter
   - the five Skills you just created
4. Save or publish the toolbox version.

### Part 5 - Attach the toolbox to the agent

1. Return to **policy-coverage-advisor**.
2. Attach the toolbox you created.
3. Save the agent configuration.

## Suggested demo prompts

### Prompt 1 - Calculation

> A claim is assessed at 2,400. Apply a 400 excess and then show the final payable amount in a
> short customer-ready explanation.

Expected behavior:

- calculation is correct
- output is concise
- wording is customer-friendly rather than internal jargon

### Prompt 2 - Claims tone

> Rewrite this response for a customer whose car was damaged in a storm: "Coverage may be subject
> to validation of endorsements and exclusions. Submit documentation."

Expected behavior:

- empathetic opening
- plain English
- no promise of payment
- clear next steps

### Prompt 3 - Disclosure footer

> Give me a coverage recommendation, then include basis, uncertainty, human review, and customer
> rights.

Expected behavior:

- distinct basis / uncertainty / review / rights structure
- clear statement that AI guidance is not the final insurer decision

### Prompt 4 - Underwriting appetite framing

> Based on this summary, recommend accept, accept with terms, refer, or decline for a small
> commercial property with incomplete sprinkler information and one recent water-loss claim.

Expected behavior:

- decision class uses the Skill's terminology
- missing evidence is listed explicitly
- likely result is **REFER** rather than an overconfident decision

## Talk track: what changed?

- **Tool** change: the agent can now calculate
- **Skill** change: the response style and governance are more consistent
- **Toolbox** change: the whole bundle is reusable for future agents

## Optional script path

If you want to accelerate setup instead of clicking through the portal:

```powershell
python -m pip install azure-ai-projects azure-identity

Copy-Item .\config.example.json .\config.json
# Edit config.json with your own placeholders replaced.

.\deploy.ps1 -WhatIf
.\deploy.ps1
.\verify.ps1
```

## Debrief questions

- Which parts belong in the agent prompt versus a Skill?
- When would you attach Code Interpreter directly versus through a toolbox?
- Which behaviors in your own domain would you centralize as Skills?
