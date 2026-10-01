# Lab - Extend the hosted-agent fallback logic

## Scenario

You already have a working offline implementation of the hosted-agent fallback pattern. In this
lab, you will extend it without calling Azure.

## Learning goal

Practice evolving orchestration logic safely by changing the **protocol detection layer first**,
then proving behavior with unit tests.

## Option A - Add a second hypothetical fallback trigger

Add support for a second, hypothetical body-level JSON-RPC condition such as:

- `error.data.code = "HostedAgentTemporarilyUnavailable"`

Suggested implementation approach:

1. Update `is_hosted_agent_not_supported()` or add a new helper that clearly separates:
   - verified current limitation
   - hypothetical extension for teaching purposes
2. Keep the current `HostedAgentNotSupported` behavior unchanged.
3. Add a new unit test that proves the new condition also routes to fallback.
4. Ensure unrelated errors still raise `A2AProtocolError`.

## Option B - Add another test case instead of changing behavior

If you want a smaller exercise:

1. Add a unit test where the JSON-RPC error contains a message/detail string mentioning
   `HostedAgentNotSupported`.
2. Confirm the helper still returns `True`.
3. Add a separate negative test for an unrelated error such as `Unauthorized`.

## Hints

- Start in `src/triage_agent/a2a_client.py`.
- Keep the fallback trigger narrow and intentional.
- Do not treat all JSON-RPC errors as retryable.
- Use only stdlib `unittest`.

## Run the lab validation

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Done-when checklist

- [ ] I can explain why HTTP 200 is insufficient for JSON-RPC orchestration.
- [ ] I changed only the offline teaching package under this module.
- [ ] I added or updated at least one unit test.
- [ ] `python -m unittest discover -s tests -p "test_*.py" -v` passes locally.
- [ ] I did not add tenant-specific values, endpoints, or secrets.

