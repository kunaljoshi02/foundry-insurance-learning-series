# Demo runbook — APIM + networking + operate capstone

This runbook is designed for a **mixed audience** and keeps the **default path offline-safe**. The only executable verification path in this module uses the local mock server in `src/` and the unit tests in `tests/`.

## Demo goals

1. Explain why a Foundry BYOM connection is often fronted by **APIM**.
2. Show the sanitized policy files and point out the **mandatory deployment-metadata probe**.
3. Prove that contract **offline** with the local mock server.
4. Close with an **operate/manage** walkthrough across all modules.
5. Introduce the **enterprise overlay** as an optional, disabled-by-default extension.

## Prerequisites

- PowerShell 7+
- Python 3.x on `PATH`
- A local `config.json` copied from `config.example.json`

> No live Azure, APIM, or Foundry calls are required for the default path.

## Part 1 — Frame the capstone

Open [README.md](README.md) and explain:

- this is **Session 8 of 8**
- the capstone is about **governance and operations**
- the private-networking overlay is **not** the default learning path

Suggested talk track:

> “We are not replacing the public course foundation. We are showing how an enterprise team would add APIM governance and, optionally, a separate private-networking overlay.”

## Part 2 — Review the sanitized APIM policies

Open:

- [infra/apim/foundry-api-policy.xml](infra/apim/foundry-api-policy.xml)
- [infra/apim/get-deployment-operation-policy.xml](infra/apim/get-deployment-operation-policy.xml)

Call out these elements:

1. **JWT validation** for caller identity
2. **Token limiting** to protect quotas and control cost
3. **URI rewriting** so the gateway presents the expected backend path
4. **Managed identity** for backend auth
5. The separate **`GET /deployments/{deploymentName}`** mock operation

## Part 3 — Preview the operator plan

Run:

```powershell
.\deploy.ps1 -WhatIf
```

Explain what the script does:

- validates `config.json`
- prints the policy files it would use
- shows how an operator could import them into their own APIM instance
- keeps enterprise overlay settings **off by default**

Optional: if you want to show the enterprise overlay gate without applying anything:

```powershell
.\deploy.ps1 -EnableEnterpriseOverlay -EnterpriseOverlayConfirmation yes-enable-enterprise-overlay -WhatIf
```

Important message:

> Even with the explicit switch and confirmation, the script only **prints** the overlay plan. It does not silently deploy private networking.

## Part 4 — Verify the deployment probe locally

Run:

```powershell
.\verify.ps1
```

What this proves:

- a `GET /deployments/<model>` request with **no `api-version`** succeeds
- the returned JSON is **ARM-shaped**
- the teaching point is validated without using a real APIM instance

If you want to show the implementation details, open:

- [src/mock_deployment_probe_server.py](src/mock_deployment_probe_server.py)
- [tests/test_deployment_probe_contract.py](tests/test_deployment_probe_contract.py)

## Part 5 — Run the offline unit tests

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Explain that the tests cover both:

- the **pure response shape**
- and the **HTTP behavior** of the local mock server

## Part 6 — Operate the whole curriculum

Open [docs/operate-checklist.md](docs/operate-checklist.md), then optionally run:

```powershell
.\verify.ps1 -RunAllModuleVerifications
```

Use this as the capstone management conversation:

- every module should have a read-only **healthy-state check**
- operators should review **tags**, **ownership**, **quota/cost**, and **known preview boundaries**
- the point of the capstone is not “more infrastructure”; it is **safe repeatability**

## Part 7 — How an operator would apply policies to a test API

This module does **not** call `az apim` by default. Instead, it prints guidance and optional command shapes.

Suggested operator sequence:

1. Create or identify a test API in APIM
2. Add a wildcard forwarding operation for your Foundry path
3. Add a dedicated `GET /deployments/{deploymentName}` operation
4. Apply:
   - `foundry-api-policy.xml` at the API level
   - `get-deployment-operation-policy.xml` on the `get-deployment` operation
5. Re-run the local probe test first, then validate against a non-production APIM instance in your own sandbox

## Enterprise overlay (optional, disabled by default)

This section is intentionally separate.

### What it adds

- a dedicated **virtual network**
- separate **agent** and **private endpoint** subnets
- a **private endpoint** for the Foundry account
- **private DNS** wiring
- an operator-reviewed plan for connecting APIM/private ingress patterns on top

### How to opt in

1. Pass `-EnableEnterpriseOverlay`
2. Type the exact confirmation string:

   ```text
   yes-enable-enterprise-overlay
   ```

3. Review the printed plan for `infra/enterprise-overlay/private-networking.bicep`

### What it does **not** do

- it does not modify `foundation/bicep/main.bicep`
- it does not silently deploy networking
- it does not replace the public baseline used by modules 01-07

## Demo close

Finish with this message:

> “The hidden APIM deployment probe is the kind of detail that derails real projects. Good operators capture those details, codify them in tests, and keep enterprise-grade networking behind an explicit gate instead of changing the default learning path.”
