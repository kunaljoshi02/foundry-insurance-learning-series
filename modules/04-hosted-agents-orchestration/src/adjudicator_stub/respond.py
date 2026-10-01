"""Tiny offline adjudicator used to simulate hosted specialist behavior in demos and tests."""
from __future__ import annotations

from typing import Any

JsonDict = dict[str, Any]


def respond(fnol: JsonDict) -> JsonDict:
    """Return a deterministic coverage-style decision for the insurance storyline."""

    narrative = str(fnol.get("fnol_narrative", "")).lower()

    if any(token in narrative for token in ("staged", "suspicious", "contradiction", "fraud")):
        return {
            "decision": "REFER TO HUMAN",
            "rationale": "Potential fraud indicators were detected in the FNOL narrative.",
            "indicative_settlement": "N/A",
            "next_actions": [
                "Escalate to SIU.",
                "Preserve statements, photos, and timeline evidence.",
            ],
        }

    if any(token in narrative for token in ("injury", "injured", "wet floor", "liability")):
        return {
            "decision": "REFER TO HUMAN",
            "rationale": "Liability or bodily injury claims require handler review in this training stub.",
            "indicative_settlement": "N/A",
            "next_actions": [
                "Collect witness details and incident report.",
                "Route to bodily injury or liability specialist.",
            ],
        }

    if "washing machine" in narrative or "burst pipe" in narrative or "water damage" in narrative:
        return {
            "decision": "COVERED",
            "rationale": "The loss appears consistent with a sudden and accidental escape-of-water scenario.",
            "indicative_settlement": "$7,800 after deductible and trace-and-access review.",
            "next_actions": [
                "Verify deductible.",
                "Request repair estimate and photos.",
            ],
        }

    return {
        "decision": "PARTIALLY COVERED",
        "rationale": "The scenario may be covered but needs clause validation and amount review.",
        "indicative_settlement": "Subject to policy wording and supporting documents.",
        "next_actions": [
            "Confirm policy wording.",
            "Obtain invoices, loss date, and proof of ownership.",
        ],
    }

