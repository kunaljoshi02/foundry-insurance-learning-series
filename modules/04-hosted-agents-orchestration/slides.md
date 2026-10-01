# Slide 1 - Session 4: Hosted agents + multi-agent orchestration

- First code-heavy module in the series
- Insurance storyline continues: triage orchestrator + adjudication specialist
- Goal: understand hosted agents, A2A, and the verified fallback pattern

---

# Slide 2 - Where we are in the course

- Modules 1-3: prompt agents, tools, skills, search grounding
- Module 4: move from prompt definitions to **hosted Python agents**
- Module 5 teaser: managed Memory

---

# Slide 3 - Prompt agents vs hosted agents

- Prompt agents: fastest path, portal-first, minimal code
- Hosted agents: Agent Framework, Python, managed hosting, packaged deployments
- Hosted agents are the right fit when you need:
  - custom orchestration logic
  - richer testing
  - code-based tool and protocol handling

---

# Slide 4 - Hosted agent basics

- Author in Python with Agent Framework
- Package through an `azd` project
- Deployed agent appears in the Foundry portal
- Can expose protocols such as Responses and A2A

---

# Slide 5 - Our two agents

- `claims-intake-triage-agent`
  - receives FNOL
  - classifies, extracts, routes
  - delegates all coverage decisions
- `coverage-settlement-adjudicator`
  - specialist for coverage rationale and settlement guidance

---

# Slide 6 - Why multi-agent here?

- Mirrors real separation of duties
- Intake agent stays customer-facing and routing-focused
- Specialist agent owns coverage logic
- Easier to reason about permissions, testing, and evolution

---

# Slide 7 - What is A2A?

- Agent-to-agent protocol for delegation
- In this module, the orchestrator sends a JSON-RPC `message/send`
- Critical lesson: transport success is not the same as agent success

---

# Slide 8 - Verified limitation: HostedAgentNotSupported

- Live observed behavior in Foundry
- A hosted agent targeted via A2A can return:
  - HTTP 200
  - JSON-RPC body with `error`
  - `error.data.code = HostedAgentNotSupported`
- Therefore: **always inspect the JSON body**

---

# Slide 9 - Detection logic

- If response has no `error`: treat as normal A2A success
- If `error.data.code` or detail indicates `HostedAgentNotSupported`:
  - raise typed signal
  - switch to hosted Responses fallback
- If error is anything else:
  - propagate it
  - do not hide it behind fallback

---

# Slide 10 - Fallback pattern

- Attempt A2A first
- Fallback only for the verified limitation
- Derive Responses endpoint from the same agent endpoint
- Log protocol, request ID, and terminal path
- Avoid logging sensitive claim text

---

# Slide 11 - Module code tour

- `a2a_client.py`
  - builds JSON-RPC request
  - detects HostedAgentNotSupported
  - invokes fallback
- `orchestrator.py`
  - simple routing wrapper
- `adjudicator_stub/respond.py`
  - offline specialist simulation

---

# Slide 12 - Unit tests to show first

- Success envelope -> no fallback
- HostedAgentNotSupported envelope -> fallback used
- Unrelated JSON-RPC error -> raised, not swallowed
- This is the core technical takeaway of Session 4

---

# Slide 13 - Demo setup

- Conceptual `azd env new`, `azd provision`, `azd deploy`
- Deploy adjudicator first
- Capture its endpoint
- Deploy triage orchestrator with adjudicator A2A endpoint configured

---

# Slide 14 - Demo narrative

- Submit FNOL narrative
- Observe A2A attempt
- Observe controlled Responses fallback
- Return adjudicator decision back through triage response

---

# Slide 15 - Key takeaways

- Hosted agents are the code-first path in Foundry Agent Service
- A2A uses JSON-RPC semantics, not just HTTP semantics
- HTTP 200 can still represent an application-level failure
- Fallback logic should be intentional, typed, and testable

---

# Slide 16 - Next module teaser

- Module 5: managed Memory
- Add cross-conversation preference recall
- Keep the same insurance storyline, now with user-scoped personalization

