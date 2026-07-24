from pathlib import Path

from ai_chatbot_qa_demo.chatbot import ToyPharmacyChatbot
from ai_chatbot_qa_demo.data_validation import load_golden_cases
from ai_chatbot_qa_demo.evaluator import evaluate_dataset, regression_gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = PROJECT_ROOT / "data" / "golden_pharmacy_cases.json"


def test_regression_gate_passes_when_chatbot_meets_quality_threshold():
    chatbot = ToyPharmacyChatbot(seed=3)
    cases = load_golden_cases(GOLDEN_PATH)

    results = evaluate_dataset(cases, chatbot.ask)
    summary = regression_gate(results, minimum_pass_rate=0.85)

    assert summary["passed"] is True
    assert summary["pass_rate"] >= 0.85
    assert summary["total_cases"] == len(cases)


def test_regression_gate_fails_when_pass_rate_is_too_low():
    fake_results = [
        {"case_id": "A", "passed": True, "failures": []},
        {"case_id": "B", "passed": False, "failures": ["bad"]},
        {"case_id": "C", "passed": False, "failures": ["bad"]},
    ]

    summary = regression_gate(fake_results, minimum_pass_rate=0.85)

    assert summary["passed"] is False
    assert summary["pass_rate"] == 1 / 3
