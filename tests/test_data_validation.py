import json
from pathlib import Path

import pytest

from ai_chatbot_qa_demo.data_validation import GoldenCaseValidationError, load_golden_cases, validate_golden_cases

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = PROJECT_ROOT / "data" / "golden_pharmacy_cases.json"


def test_golden_dataset_has_required_fields_and_valid_guardrails():
    cases = load_golden_cases(GOLDEN_PATH)

    assert len(cases) >= 5
    validate_golden_cases(cases)


def test_data_validation_rejects_missing_expected_intent():
    broken_case = {
        "id": "BROKEN-001",
        "user_message": "hello",
        "expected_business_outcome": "some_outcome",
        "must_include_concepts": [],
        "forbidden_concepts": [],
        "guardrails": {"must_refuse": False},
    }

    with pytest.raises(GoldenCaseValidationError, match="expected_intent"):
        validate_golden_cases([broken_case])


def test_data_validation_rejects_duplicate_case_ids(tmp_path):
    cases = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    cases.append(dict(cases[0]))

    with pytest.raises(GoldenCaseValidationError, match="Duplicate case id"):
        validate_golden_cases(cases)
