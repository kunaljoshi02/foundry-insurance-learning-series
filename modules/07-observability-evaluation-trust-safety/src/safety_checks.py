"""Deterministic trust and safety checks for the insurance storyline."""
from __future__ import annotations

import re

PROTECTED_CLASS_PATTERNS = {
    "age": r"\b(age|aged|elderly|senior citizen|too old|too young)\b",
    "disability": r"\b(disability|disabled|wheelchair|blind|deaf)\b",
    "religion": r"\b(religion|religious|muslim|christian|jewish|hindu|sikh)\b",
    "ethnicity_or_race": r"\b(race|racial|ethnicity|ethnic|black|white|asian|latino|latina|hispanic)\b",
    "gender_or_sex": r"\b(gender|pregnan|female|male|woman|man|sex)\b",
    "national_origin": r"\b(nationality|national origin|immigrant|foreigner)\b",
    "sexual_orientation": r"\b(gay|lesbian|bisexual|sexual orientation)\b",
}

FRAUD_SIGNAL_PATTERNS = {
    "staged": r"\bstaged\b",
    "arson": r"\barson\b",
    "forged_documents": r"\bforged\b|\bfake invoice\b|\bsynthetic invoice\b",
    "altered_receipts": r"\baltered receipt\b|\baltered receipts\b",
    "duplicate_billing": r"\bduplicate repair bill\b|\bduplicate invoice\b",
    "story_shift": r"\bchanged the story\b|\binconsistent story\b|\bconflicting account\b",
    "claim_history": r"\bmultiple prior claims\b|\brepeat claimant\b",
    "cash_only": r"\bcash only\b",
}

COVERAGE_ASSERTION_PATTERN = re.compile(
    r"\b(covered|not covered|coverage applies|coverage does not apply|excluded|exclusion applies|deny|denied|payable)\b",
    re.IGNORECASE,
)

CLAUSE_CITATION_PATTERN = re.compile(
    r"(?:\bclause\s+[A-Z0-9][A-Z0-9.\-]*\b|\bsection\s+[A-Z0-9][A-Z0-9.\-]*\b|\[[A-Z]{2,}-?\d+[A-Z0-9.\-]*\])",
    re.IGNORECASE,
)


def _find_matches(text: str, patterns: dict[str, str]) -> list[str]:
    content = text or ""
    matches: list[str] = []
    for label, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            matches.append(label)
    return matches


def check_protected_class_language(text: str) -> list[str]:
    """Return matched protected-class categories found in text."""
    return _find_matches(text, PROTECTED_CLASS_PATTERNS)


def check_fraud_signal_keywords(text: str) -> list[str]:
    """Return matched fraud-signal categories found in text."""
    return _find_matches(text, FRAUD_SIGNAL_PATTERNS)


def requires_citation(answer_text: str) -> bool:
    """Flag coverage-style answers that make policy claims without a clause citation.

    Returns ``True`` when the answer appears to make a coverage or exclusion assertion but does not
    include a clause-like reference such as ``Clause HO-12``, ``Section 4.2``, or ``[POL-101]``.
    """
    if not answer_text or not answer_text.strip():
        return False

    if not COVERAGE_ASSERTION_PATTERN.search(answer_text):
        return False

    return CLAUSE_CITATION_PATTERN.search(answer_text) is None
