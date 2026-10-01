# Slide 1 — Session 8 capstone

- **APIM + private networking + manage/operate**
- Final session in the Foundry Insurance Learning Series
- Goal: tie architecture, governance, verification, and operator thinking together

---

# Slide 2 — What this capstone solves

- We already built agents, tools, search, orchestration, memory, identity, and observability
- Now we answer the operator questions:
  - How do we **front model traffic**?
  - How do we **govern tokens and access**?
  - How do we **verify the full curriculum**?
  - How do we explain **private networking** without changing the public training base?

---

# Slide 3 — Why front Foundry with APIM?

- Central place for **authentication and authorization**
- Apply **consistent policy** across multiple model-consuming apps
- Add **token quotas / rate controls**
- Emit **gateway-level metrics**
- Create a reviewable path for enterprise security and platform teams

---

# Slide 4 — BYOM connection basics

- Foundry can consume a model endpoint as a **Bring Your Own Model** connection
- APIM can sit in front of that endpoint and become the governed target
- Typical policy chain:
  - validate incoming JWT
  - enforce token limits
  - rewrite to the backend path shape
  - authenticate to the backend with managed identity

---

# Slide 5 — APIM policy chain for this module

- `validate-azure-ad-token`
- `llm-token-limit`
- optional token metrics / headers
- `set-backend-service`
- `rewrite-uri`
- `authentication-managed-identity`
- operator-friendly comments in sanitized XML

---

# Slide 6 — Architecture at a glance

- Client or portal caller
- APIM gateway
- BYOM policy chain
- Foundry model connection
- Backend model endpoint

Message: **the gateway is part of the model contract, not just a pass-through proxy**

---

# Slide 7 — The memorable gotcha

## Foundry does a hidden validation probe

- `GET {target}/deployments/{model}`
- **No `api-version`**
- Expects an **ARM Cognitive Services deployment resource**

If that probe is missing or shaped incorrectly, calls can fail with a bare **`NotFound`**.

---

# Slide 8 — What “ARM-shaped” means

Required response ideas:

- `id`
- `name`
- `type = Microsoft.CognitiveServices/accounts/deployments`
- `sku`
- `properties.model.name`
- `properties.model.format`
- `properties.model.version`
- `properties.provisioningState = Succeeded`

Not enough: an OpenAI-style deployment object

---

# Slide 9 — Why this matters operationally

- Debugging looks misleading: chat calls fail later, but the root cause is the metadata probe
- Teams often implement only chat/completions forwarding
- The fix is simple once known, but expensive if undocumented
- This is why the capstone includes an **offline probe contract test**

---

# Slide 10 — Offline verification path

- Local stdlib mock server simulates the APIM `get-deployment` response
- `verify.ps1`:
  - starts the mock server
  - sends `GET /deployments/<model>`
  - asserts ARM-shaped JSON
- `python -m unittest` validates the same contract in code

---

# Slide 11 — Operate/manage checklist across all 8 modules

- Run each module’s `verify.ps1`
- Confirm consistent tags:
  - `course=foundry-insurance-learning-series`
  - `owner=<team-or-alias>`
- Check gateway/model quotas and Search costs
- Review observability and guardrail signals
- Document known preview boundaries honestly

---

# Slide 12 — Enterprise overlay concept

- **Optional**
- **Explicitly gated**
- **Disabled by default**
- Separate Bicep file, not wired into the shared foundation

It demonstrates:

- VNet + subnet pattern
- private endpoints
- private DNS
- operator-controlled rollout

---

# Slide 13 — Why keep the overlay separate?

- Modules 01-07 depend on a **public learning base**
- Silent networking changes would break the course flow
- Enterprise networking belongs in an **overlay**, not the default path
- This mirrors real platform engineering: additive, reviewable, gated change

---

# Slide 14 — Cost and ownership reminders

- APIM adds a gateway cost surface
- Token limits are governance and cost-control tools
- Keep demo tiers intentional
- Clean ownership tags reduce cleanup risk
- Use read-only checks before destructive changes

---

# Slide 15 — Capstone storyline recap

- Module 1: first agent
- Module 2: tools and Skills
- Module 3: grounding
- Module 4: orchestration
- Module 5: memory
- Module 6: identity
- Module 7: observability and trust
- Module 8: gateway + operations + enterprise framing

---

# Slide 16 — Key takeaways

- APIM is a strong governance layer for Foundry BYOM traffic
- The **deployment-metadata probe** is real, mandatory, and easy to miss
- Operating the solution means more than deployment: tags, cost, verification, and honesty about boundaries
- Private networking should be **opt-in**, **reviewed**, and **disabled by default** in a training repo
