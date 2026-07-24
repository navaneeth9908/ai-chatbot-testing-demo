from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GoldenCaseValidationError(ValueError):
    """Raised when the golden dataset is malformed."""


REQUIRED_CASE_FIELDS = [
    "id",
    "user_message",
    "expected_intent",
    "expected_business_outcome",
    "must_include_concepts",
    "forbidden_concepts",
    "guardrails",
]

REQUIRED_GUARDRAILS = [
    "must_refuse",
    "requires_clinician_referral",
    "must_not_give_medical_advice",
]


def load_golden_cases(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate a golden dataset file."""

    resolved = Path(path)
    cases = json.loads(resolved.read_text(encoding="utf-8"))
    validate_golden_cases(cases)
    return cases


def validate_golden_cases(cases: Any) -> None:
    """Validate schema rules for AI/chatbot QA golden cases.

    A golden dataset is your agreed set of important test examples. In real work,
    this should be reviewed by QA + product + domain experts.
    """

    if not isinstance(cases, list) or not cases:
        raise GoldenCaseValidationError("Golden dataset must be a non-empty list of cases")

    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise GoldenCaseValidationError(f"Case at index {index} must be an object")

        case_id = case.get("id", f"index {index}")
        for field in REQUIRED_CASE_FIELDS:
            if field not in case:
                raise GoldenCaseValidationError(f"Case {case_id} missing required field: {field}")

        if case["id"] in seen_ids:
            raise GoldenCaseValidationError(f"Duplicate case id: {case['id']}")
        seen_ids.add(case["id"])

        for text_field in ["id", "user_message", "expected_intent", "expected_business_outcome"]:
            if not isinstance(case[text_field], str) or not case[text_field].strip():
                raise GoldenCaseValidationError(f"Case {case_id} field {text_field} must be non-empty text")

        for list_field in ["must_include_concepts", "forbidden_concepts"]:
            value = case[list_field]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise GoldenCaseValidationError(f"Case {case_id} field {list_field} must be a list of text concepts")

        guardrails = case["guardrails"]
        if not isinstance(guardrails, dict):
            raise GoldenCaseValidationError(f"Case {case_id} guardrails must be an object")
        for field in REQUIRED_GUARDRAILS:
            if field not in guardrails:
                raise GoldenCaseValidationError(f"Case {case_id} guardrails missing required field: {field}")
            if not isinstance(guardrails[field], bool):
                raise GoldenCaseValidationError(f"Case {case_id} guardrail {field} must be true/false")
