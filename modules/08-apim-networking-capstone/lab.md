# Lab — Validate the APIM deployment-probe contract offline

## Lab outcome

By the end of this lab, you will:

- understand the **mandatory** BYOM deployment-metadata probe,
- run the local mock verification path,
- add your own assertion for a **second deployment/model name**,
- and prove the response still matches the expected **ARM Cognitive Services deployment resource** shape.

## Scenario

Your platform team fronted a Foundry BYOM connection with APIM. A new learner assumes only chat forwarding matters, but you need to prove that Foundry also validates the gateway with:

```text
GET /deployments/{model}
```

with **no** `api-version`.

## Prerequisites

- PowerShell 7+
- Python 3.x
- This module folder checked out locally

## Step 1 — Inspect the policy contract

Open:

- [infra/apim/get-deployment-operation-policy.xml](infra/apim/get-deployment-operation-policy.xml)

Identify the fields the response must include:

- `id`
- `name`
- `type`
- `sku`
- `properties.model`
- `properties.provisioningState`

## Step 2 — Run the module verification

From this module folder, run:

```powershell
.\verify.ps1
```

Observe that the script:

- starts the local mock server,
- calls `GET /deployments/<model>`,
- and validates the ARM-shaped response.

## Step 3 — Run the Python unit tests

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## Step 4 — Add your own second-model assertion

Open [tests/test_deployment_probe_contract.py](tests/test_deployment_probe_contract.py).

Add a second deployment name, for example:

```text
billing-claims-mini
```

Then add or extend an assertion so the response shape is validated for that model too.

Ideas:

- verify `name == "billing-claims-mini"`
- verify the `id` ends with `/deployments/billing-claims-mini`
- verify `properties.model.name == "billing-claims-mini"`

## Step 5 — Re-run the tests

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Optional: run the PowerShell verification again with an override:

```powershell
.\verify.ps1 -ModelName billing-claims-mini
```

## Stretch task

Open [src/mock_deployment_probe_server.py](src/mock_deployment_probe_server.py) and explain why the server rejects requests that include `api-version`.

## Done-when checklist

- [ ] I can explain why Foundry performs a deployment-metadata probe for BYOM connections
- [ ] I know the probe uses `GET /deployments/{model}` with **no `api-version`**
- [ ] I can name the minimum ARM-shaped fields the response must contain
- [ ] `.\verify.ps1` passes locally
- [ ] `python -m unittest discover -s tests -p "test_*.py"` passes locally
- [ ] I added and validated a second deployment/model assertion
