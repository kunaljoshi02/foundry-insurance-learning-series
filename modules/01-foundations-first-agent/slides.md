# Slide 1 — Welcome to Session 1

**Foundations + first prompt agent**

- Session 1 of 8 in the Microsoft Foundry insurance storyline
- Goal: move from platform concepts to a working agent in one sitting
- Audience: business stakeholders + developers
- Delivery style: portal-first, scripts optional

---

# Slide 2 — Agenda

- What Microsoft Foundry is
- Core building blocks: account, project, model deployment, playground
- What an agent is in Foundry
- Create the first insurance prompt agent
- Test it live in the portal
- Preview where modules 2–8 take us next

---

# Slide 3 — What is Microsoft Foundry?

- A unified platform for **models, agents, tools, and operations**
- Designed for both quick prototyping and enterprise-ready builds
- Gives one place to manage:
  - project-scoped AI assets
  - model access
  - agent behavior
  - later: tracing, evaluation, and governance

**Message for stakeholders:** this is the product surface.  
**Message for developers:** this is the runtime and control plane you will build against.

---

# Slide 4 — Foundry vocabulary for this course

- **Foundry account**: top-level Azure resource
- **Foundry project**: where learners work day to day
- **Model deployment**: named deployed model the agent uses
- **Playground**: safe place to test prompts, agents, and responses

**Mental model:** account contains project; project uses model deployment; playground helps validate behavior.

---

# Slide 5 — What is an agent?

- An agent is reusable behavior, not just a single prompt
- In this course, the important ingredients are:
  - **instructions**
  - **model**
  - **tools** *(preview only today)*
  - **conversation/thread history**
  - **responses/runs**

Today we stay intentionally simple: **instructions + model + conversation**.

---

# Slide 6 — Prompt agent vs later agent types

**Prompt agent today**

- Declarative
- Fast to build in portal
- Great for persona, formatting, boundaries, and workflow guidance

**Later modules**

- tools and toolbox composition
- search grounding
- hosted agents
- multi-agent orchestration
- memory and identity

---

# Slide 7 — Insurance storyline entry point

First agent: **`policy-coverage-advisor`**

- Persona: plain-English insurance assistant
- Purpose: answer general policy coverage questions
- Guardrails:
  - no customer-specific promises
  - no invented limits or clause numbers
  - escalate certainty-sensitive questions to a human

This is a teaching agent, not a production adjudicator.

---

# Slide 8 — Demo flow

1. Open the shared Foundry project
2. Verify the chat model deployment from foundation
3. Create a prompt agent in the portal
4. Paste the system instructions
5. Test with sample questions in the playground

Optional accelerator: `deploy.ps1`

---

# Slide 9 — Suggested playground questions

- “Does a standard homeowners policy usually cover kitchen fire damage?”
- “Is flood damage normally included or separate?”
- “What information would you need before answering a stolen bicycle question?”
- “Can you guarantee this claim will be paid?”

What we want to see:

- plain-English answers
- clear uncertainty handling
- no hallucinated policy specifics
- consistent persona

---

# Slide 10 — Threads, conversations, and runs

- **Agent** = reusable behavior definition
- **Conversation/thread** = persisted context over turns
- **Run/response** = one execution against the conversation

Why it matters:

- stakeholders see continuity across follow-up questions
- developers see how stateful interactions are modeled

---

# Slide 11 — What learners should notice

- The same model can behave very differently based on instructions
- Good agent behavior starts with scope and boundaries
- Portal creation lowers the entry barrier before writing code
- This session creates the baseline for all later modules

---

# Slide 12 — What comes next in Module 2

**Tools, Skills & toolbox**

- add built-in and managed tools
- separate “what the agent knows” from “what the model guesses”
- compose reusable capability sets for multiple agents

Today’s teaser: tools exist, but we intentionally keep them out of this first build.

---

# Slide 13 — Key takeaways

- Foundry organizes work around **accounts, projects, models, and agents**
- A prompt agent is the fastest way to create a first useful assistant
- Today’s `policy-coverage-advisor` is intentionally simple
- The rest of the curriculum layers enterprise features on top of this baseline
