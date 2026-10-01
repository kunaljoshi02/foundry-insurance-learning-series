# Privacy notes for Module 05

This module demonstrates **managed Memory** in Microsoft Foundry Agent Service. The goal is to
teach useful personalization **without** turning the demo into a real-data storage exercise.

## What must never be stored in memory in this curriculum

Use **synthetic** training content only.

Do **not** store:

- real customer names
- claim numbers from live systems
- addresses or contact details
- payment card or bank data
- health or medical details
- credentials, tokens, or secrets
- protected-class attributes
- any other real PII or regulated claim content

Acceptable examples for this curriculum are limited to low-risk preferences such as:

- answer format
- bullet vs. paragraph style
- ordering preferences
- example-currency preference

## How scope-per-identity works

Managed Memory is intended to be partitioned **per user identity** rather than shared across all
learners. In practice:

- the signed-in user's identity determines which memory scope is used,
- one user's preferences should not automatically appear for another user,
- privacy demonstrations should erase **one user's** scope, not everyone else's data.

For backend or proxy-led patterns, the effective user scope may need to be passed explicitly. In
portal-led demos, the portal commonly resolves the signed-in identity automatically.

## Privacy demonstration guidance

When teaching this module:

1. store only low-risk synthetic preferences,
2. show that the agent recalls them across conversations for the same user,
3. show how to clear that user's memory,
4. verify the recall is gone,
5. avoid browsing through unrelated memory contents.

## Security reference

For the repository-wide no-secrets / no-tenant-specific-data policy, see
[../../../SECURITY.md](../../../SECURITY.md).
