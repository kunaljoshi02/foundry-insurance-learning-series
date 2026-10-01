"""Thin FNOL orchestration helpers used by the training module.

The goal here is not to replicate the full hosted runtime. Instead, the module gives learners a
small, runnable package that demonstrates routing plus the verified A2A-to-Responses fallback
contract in pure Python.
"""
from __future__ import annotations

from typing import Any

from .a2a_client import FallbackCallable, InvocationOutcome, Transport, invoke_with_fallback

JsonDict = dict[str, Any]


def classify_route(fnol_narrative: str) -> str:
    """Map a free-text FNOL narrative into the course's three routing buckets."""

    narrative = fnol_narrative.lower()

    fraud_markers = ("staged", "suspicious", "contradiction", "inconsistent", "fraud")
    if any(marker in narrative for marker in fraud_markers):
        return "fraud-escalation"

    complex_markers = ("injury", "injured", "lawsuit", "attorney", "liability", "hospital")
    if any(marker in narrative for marker in complex_markers):
        return "manual-review"

    return "auto-adjudicate"


def triage_fnol(
    fnol: JsonDict,
    *,
    adjudicator_a2a_url: str,
    transport: Transport | None = None,
    fallback_callable: FallbackCallable,
) -> JsonDict:
    """Route a claim and attach the adjudicator result returned by the chosen protocol."""

    narrative = str(fnol.get("fnol_narrative", ""))
    route = classify_route(narrative)
    adjudication: InvocationOutcome = invoke_with_fallback(
        adjudicator_a2a_url,
        fnol,
        transport=transport,
        fallback_callable=fallback_callable,
    )
    return {
        "route": route,
        "used_fallback": adjudication.used_fallback,
        "protocol": adjudication.protocol,
        "request_id": adjudication.request_id,
        "adjudicator_result": adjudication.result,
    }

