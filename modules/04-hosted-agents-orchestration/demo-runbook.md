# Demo runbook - Hosted agents + multi-agent orchestration

This runbook is a **concept walkthrough**. It describes commands learners run themselves in their
own Azure context. Nothing in this module executes `az`, `azd`, or a live agent call for you.

## Demo objective

Show a hosted **triage orchestrator** delegating to a hosted **adjudicator specialist**, detect the
verified `HostedAgentNotSupported` JSON-RPC envelope, and fall back to the specialist's hosted
Responses endpoint.

## Before the demo

1. Complete modules 1-3 so the audience already understands prompt agents, tools, and grounding.
2. Populate `config.json` from `config.example.json`.
3. Review the offline unit test first:

   ```powershell
   python -m unittest discover -s tests -p "test_*.py" -v
   ```

4. Tell the audience the limitation up front:
   - A2A to a hosted target currently requires body inspection.
   - HTTP 200 does **not** guarantee success.

## Conceptual deployment order

### Step 1 - Deploy the adjudicator

From your adjudicator hosted-agent project:

```powershell
azd env new <module04-env>-adj
azd env set FOUNDRY_PROJECT_ENDPOINT <foundry-project-endpoint>
azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME <chat-model-deployment>
azd provision
azd deploy
```

Expected outcome:

- hosted adjudicator appears in the Foundry portal
- protocol surface includes Responses, and possibly A2A if configured

### Step 2 - Capture the adjudicator endpoint

Record the adjudicator's hosted endpoint values you need for the triage deployment:

- hosted Responses endpoint
- A2A endpoint (if exposed)

Do not paste real tenant-specific values into this repository or slides.

### Step 3 - Deploy the triage orchestrator

From your triage hosted-agent project:

```powershell
azd env new <module04-env>-triage
azd env set FOUNDRY_PROJECT_ENDPOINT <foundry-project-endpoint>
azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME <chat-model-deployment>
azd env set ADJUDICATOR_A2A_URL <adjudicator-a2a-endpoint>
azd provision
azd deploy
```

Expected outcome:

- triage hosted agent appears in the Foundry portal
- the orchestrator is configured to try A2A first

## How to invoke the triage agent

Use the Foundry portal or your own client to submit a claim narrative similar to:

> Policy HOME-1001. The customer says a washing machine hose burst overnight and flooded the
> kitchen. Estimated damage is 8200 dollars plus 1400 dollars to locate and expose the leak. No
> injuries were reported and the loss was reported the same day.

## What to watch for during the demo

### Expected orchestration sequence

1. Triage agent receives the FNOL narrative.
2. Triage agent constructs a blocking A2A JSON-RPC `message/send`.
3. Service returns HTTP 200 **with** a JSON-RPC error envelope.
4. The body indicates `HostedAgentNotSupported`.
5. Triage agent logs that it is switching protocols.
6. Triage agent calls the adjudicator's hosted Responses endpoint.
7. Adjudicator returns a coverage decision and indicative settlement guidance.
8. Triage agent includes that decision in its final response.

### Example trace/log cues

Look for messages conceptually similar to:

- `Sending blocking A2A message/send`
- `Received HTTP 200 from A2A transport`
- `Detected HostedAgentNotSupported in JSON-RPC body`
- `Retrying adjudicator over hosted Responses endpoint`
- `Fallback completed; protocol=responses`

Avoid logging raw claim content in shared screenshots.

## Expected learner-facing result

The final response should show:

- a triage summary
- extracted entities
- routing decision
- adjudicator findings
- recommended next actions

For the sample water-damage narrative, an expected result is:

- route: `auto-adjudicate`
- adjudicator decision: `COVERED`
- rationale: sudden and accidental water loss pattern
- settlement guidance: indicative amount after deductible / trace-and-access review

## Portal talking points

- Hosted agents show up as deployed assets in the Foundry portal.
- This is still a Foundry-native experience, even though the logic is code-first.
- The demo is more compelling if learners see both:
  - the portal asset view
  - the Python logic that made the protocol decision

## If the demo time is short

Use this compressed flow:

1. show `tests/test_a2a_fallback.py`
2. run offline unittest
3. show the architecture diagram from `README.md`
4. explain the deployment steps verbally

