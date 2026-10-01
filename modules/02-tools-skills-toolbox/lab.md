# Lab - Create and attach your own Skill

In this lab, learners create one extra Skill and attach it to the same insurance advisor pattern.

## Goal

Create a new Skill named **claims-empathy-tone** that makes difficult claims messages warmer and
clearer without admitting liability or promising payment.

## What learners practice

- writing a simple `SKILL.md`
- creating a versioned Skill in the portal
- attaching it through an agent or toolbox
- testing the behavior change with side-by-side prompts

## Starting point

Assume the learner already has:

- access to the Foundry project
- an existing **policy-coverage-advisor**
- the toolbox from this module, or at least the ability to add one Skill manually

## Instructions

### Step 1 - Draft the Skill

Create a `SKILL.md` with:

- front matter:
  - `name: claims-empathy-tone`
  - short description
- guidance such as:
  - acknowledge the event first
  - use plain English
  - keep sentences short
  - avoid blame
  - do not promise payment
  - give clear next steps

### Step 2 - Create the Skill in Foundry

1. Open the Skills experience in the portal.
2. Create a new Skill.
3. Paste or upload the `SKILL.md`.
4. Save the version.

### Step 3 - Attach it

Choose one of two paths:

- **Agent-only path:** attach the Skill directly to the agent.
- **Reusable path:** add it to a toolbox version, then attach the toolbox to the agent.

### Step 4 - Test it

Run this prompt before and after attaching the new Skill:

> The customer is upset after a burst pipe damaged their flooring. Ask for the next three pieces
> of information we need.

### Step 5 - Compare outputs

Look for:

- stronger empathy
- clearer next steps
- less jargon
- no promise that the claim will be paid

## Done-when checklist

- [ ] I created a valid `SKILL.md` with front matter and clear instructions.
- [ ] I created a Skill version in the portal.
- [ ] I attached the Skill to the agent directly or through a toolbox.
- [ ] I tested the agent with the same prompt before and after.
- [ ] I can explain how a Skill differs from the base agent prompt.
- [ ] I can explain why a toolbox is better when multiple agents need the same behavior.

## Stretch goal

Create a second Skill that changes the output structure, for example:

- a **decision-summary** Skill that always returns answer / basis / uncertainty / next steps
- or a **broker-tone** Skill aimed at intermediary communications instead of claimant messaging

## Reflection

When would you:

1. keep behavior in the agent prompt,
2. move it into a Skill,
3. or place it in a shared toolbox for reuse across several agents?
