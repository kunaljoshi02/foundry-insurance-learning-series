# Demo runbook - Module 7

This runbook stays offline by default. It demonstrates how to **author in observability**, run the offline evaluator, and inspect simple trust/safety checks without calling Azure resources.

## Audience promise

- Developer-leaning for the OTel and evaluator code
- Business-relevant for trust, fraud escalation, and grounded coverage decisions

## 1. Introduce the theme

Frame the session as: **"We already built agent behavior. Now we make it operable, measurable, and safer."**

Key talking points:

- tracing tells you what happened inside the agent
- evaluation tells you whether routing behavior matches expectation
- trust/safety rules keep outputs reviewable and policy-aware
- optimization uses both telemetry and evaluation as feedback

## 2. Show the authoring-time OTel pattern

Open [`src/otel_setup.py`](src/otel_setup.py) and walk through these three entry points:

1. `configure_otel(...)`
   - creates a tracer provider
   - adds Azure Monitor exporter only when a connection string and package are available
   - never blocks local execution when telemetry is unavailable
2. `start_agent_run_span(name, **attributes)`
   - creates a root span around an agent run
   - records business-friendly attributes such as route, policy number, or conversation mode
3. `@instrument_tool_call`
   - wraps a tool function with a consistent child span
   - works for sync and async functions
   - records errors on the span before re-raising

### Conceptual triage example

```python
from otel_setup import configure_otel, instrument_tool_call, start_agent_run_span

configure_otel(service_name="claims-triage-agent")

@instrument_tool_call
def lookup_policy(policy_number: str) -> dict:
    return {"policy_number": policy_number, "status": "active"}


def run_triage(case: dict) -> str:
    with start_agent_run_span("triage", policy_number=case.get("policy_number", "<unknown>")):
        lookup_policy(case.get("policy_number", "<unknown>"))
        return "manual-review"
```

### Conceptual adjudicator example

```python
from otel_setup import configure_otel, instrument_tool_call, start_agent_run_span

configure_otel(service_name="coverage-settlement-adjudicator")

@instrument_tool_call
async def calculate_payable(amount: float, excess: float) -> float:
    return max(amount - excess, 0)


async def run_adjudication(claim: dict) -> float:
    with start_agent_run_span("adjudication", route="auto-adjudicate"):
        return await calculate_payable(claim["loss_amount"], claim["excess"])
```

Use this moment to contrast with the anti-pattern from the field: **patching telemetry into already-deployed code after a demo goes dark**.

## 3. Call out the verified field notes

Use the summary in [`README.md`](README.md) and keep the language sanitized:

- App Insights can stay empty because of ingestion/network design, not because the agent stopped working.
- RBAC matters, but it is only one condition for successful telemetry.
- Hosted agents often need explicit exporter wiring and HTTP instrumentation.
- APIM token metrics require an explicit metric-emission policy.
- Endpoint/versioning rules can differ across prompt and hosted-agent surfaces.

Label these as **verified field notes**, not mandatory lab steps.

## 4. Run the offline evaluator harness

From this module folder:

```powershell
python .\src\evaluator.py --output .\artifacts\scorecard.json
```

What to show:

- the dataset lives in [`eval/triage-eval-dataset.json`](eval/triage-eval-dataset.json)
- each case includes `test_case_description`
- the console summary gives total, passed, failed, and pass rate
- the JSON scorecard is easy to inspect or gate in CI

### What the evaluator is doing

- loads the dataset
- applies a pluggable routing function
- defaults to a rule-based offline router
- compares actual route with `expected.route`
- produces per-case detail for discussion and debugging

### Optional live mode (do not run by default)

The evaluator supports an explicit live mode for advanced learners:

```powershell
python .\src\evaluator.py --live --router my_router_module:route_case
```

Explain that this mode is **opt-in only** and intentionally not used in the module's default verification path.

## 5. Show the safety checks

Run a few quick examples:

```powershell
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('src').resolve())); import safety_checks as s; print(s.check_fraud_signal_keywords('The claimant changed the story twice and submitted altered receipts.')); print(s.check_protected_class_language('Decline because the driver is elderly.')); print(s.requires_citation('The loss is excluded under the policy.'))"
```

Interpretation:

- fraud signals should trigger review or escalation, not automatic confidence
- protected-class wording should be flagged for human review
- coverage/exclusion claims without a clause reference should fail the citation check

## 6. Connect evaluation to optimization

Use one failed or hypothetical case and ask:

- Is this a routing-rule problem?
- Is the prompt missing a clearer fraud escalation instruction?
- Is a tool description too broad?
- Do we need a stronger citation requirement?

The answer is usually **change the narrowest reliable layer first**.

## 7. Close the demo

Summarize the operating model:

1. instrument in code
2. verify offline
3. enforce explicit trust/safety rules
4. improve with a repeatable dataset

Then preview Module 8 as the networking and APIM operating capstone.
