import json
from pathlib import Path

from ai_chatbot_qa_demo.chatbot import ChatbotResponse, ToyPharmacyChatbot
from ai_chatbot_qa_demo.evaluator import evaluate_response

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = PROJECT_ROOT / "data" / "golden_pharmacy_cases.json"


def _case(case_id: str) -> dict:
    cases = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    return next(case for case in cases if case["id"] == case_id)


def test_non_deterministic_wording_validates_by_intent_and_business_outcome_not_exact_text():
    case = _case("PHARM-001")

    response_a = ChatbotResponse(
        text="Sure — I can start a refill. Please share your member ID and prescription number.",
        intent="refill_request",
        business_outcome="starts_refill_workflow",
    )
    response_b = ChatbotResponse(
        text="I can begin renewing your Rx. I will need your member number first.",
        intent="refill_request",
        business_outcome="starts_refill_workflow",
    )

    assert response_a.text != response_b.text
    assert response_a.text != case["reference_answer"]
    assert response_b.text != case["reference_answer"]

    assert evaluate_response(case, response_a).passed
    assert evaluate_response(case, response_b).passed


def test_guardrail_catches_unsafe_drug_interaction_answer():
    case = _case("PHARM-002")
    unsafe_response = ChatbotResponse(
        text="Yes, it is safe to take them together tonight. No need to ask anyone.",
        intent="drug_interaction_question",
        business_outcome="answers_medical_question_directly",
    )

    result = evaluate_response(case, unsafe_response)

    assert not result.passed
    assert any("business outcome" in failure.lower() for failure in result.failures)
    assert any("forbidden concept" in failure.lower() for failure in result.failures)


def test_toy_chatbot_passes_pharmacy_refill_case_without_exact_wording_check():
    chatbot = ToyPharmacyChatbot(seed=7)
    case = _case("PHARM-001")

    response = chatbot.ask(case["user_message"])
    result = evaluate_response(case, response)

    assert response.text != case["reference_answer"]
    assert result.passed, result.failures
