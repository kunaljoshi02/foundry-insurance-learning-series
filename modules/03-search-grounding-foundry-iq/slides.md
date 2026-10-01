# Slide 1 — Session 3: Grounding the insurance advisor

**Azure AI Search grounding / Foundry IQ patterns**

- Session 3 of 8
- Same storyline, same agent, new capability
- Goal: move from plausible answers to **clause-backed answers**

---

# Slide 2 — Why grounding matters

- Insurance questions often depend on **exact wording**
- A fluent answer without source retrieval can still be wrong
- Hallucination risk is high when the model guesses:
  - limits
  - exclusions
  - conditions precedent
  - endorsements

**Key message:** confidence is not evidence.

---

# Slide 3 — What changes from Modules 1-2?

Before today, `policy-coverage-advisor` had:

- instructions
- optional Skills
- optional toolbox behavior

After today, it also has:

- a **Search-backed corpus**
- a **project connection**
- a **grounding tool** that retrieves relevant clauses

---

# Slide 4 — The policy corpus for this session

Shared dataset: `policy-wordings.json`

- 36 synthetic insurance clauses
- Home, Motor, and Liability products
- realistic structure for:
  - definitions
  - cover grants
  - exclusions
  - conditions
  - limits

Each clause becomes one retrieval document.

---

# Slide 5 — Search index concepts learners should know

- **Fields**: structured attributes such as `product`, `section_ref`, and `clause_type`
- **Searchable text**: `title` and `content`
- **Filterable metadata**: product, form, clause type
- **Vector field**: placeholder for semantic similarity search
- **Semantic ranking / hybrid**: combines lexical and semantic signals

---

# Slide 6 — Keyword, vector, and hybrid retrieval

**Keyword**
- great for exact clause IDs and policy terms

**Vector**
- great for “same meaning, different wording” questions

**Hybrid**
- often the practical sweet spot
- combines exact matching with semantic relevance

This module explains all three, while keeping the live demo simple and teachable.

---

# Slide 7 — Architecture at a glance

1. Shared JSON corpus
2. Build/upload script
3. Azure AI Search index
4. Foundry project connection
5. Azure AI Search tool on the agent
6. Answer with citations

**Mental model:** source -> retrieval -> grounded response.

---

# Slide 8 — What we mean by “Foundry IQ”

In this course, “Foundry IQ” means:

- retrieval-backed grounding for trusted enterprise content
- managed by Foundry Agent Service runtime components
- designed to help the model answer from evidence, not memory alone

Use current Learn docs for exact scope, labels, and preview status.

---

# Slide 9 — Demo flow

1. Ask a clause-specific question before grounding
2. Provision or confirm Azure AI Search
3. Build the index from `policy-wordings.json`
4. Add the Search connection in Foundry
5. Attach the tool to `policy-coverage-advisor`
6. Re-run the question and inspect citations

---

# Slide 10 — Sample grounded questions

- “Does trace and access cover opening the building to find a leak?”
- “If the driver was delivering food, is own-damage cover excluded?”
- “What wording matters for a customer slipping on a wet floor?”

Look for answers that reference clauses such as:

- `HOME-2-4`
- `MOTOR-5-1`
- `LIAB-6-2`

---

# Slide 11 — Current limitations / caveats to say out loud

- Portal labels and grounding workflows can evolve
- Some Foundry knowledge experiences are still changing quickly
- Search connections and tool setup vary by environment and authentication model
- Learn docs, not slide text, are the source of truth for current-state specifics

---

# Slide 12 — Key takeaways

- Grounding reduces hallucination risk for policy questions
- Azure AI Search gives us structured retrieval over the clause corpus
- The agent runtime can turn search results into **citation-backed answers**
- This is the turning point from prompt-only guidance to evidence-backed guidance

---

# Slide 13 — Next up: Module 4

**Hosted agents + multi-agent orchestration**

- split responsibilities across specialist agents
- move beyond one grounded advisor
- introduce handoff/orchestration patterns for insurance workflows
