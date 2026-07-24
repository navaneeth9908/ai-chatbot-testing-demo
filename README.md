# AI / Chatbot Testing Demo Project

This is a beginner-friendly example project for an AI QA / ML QA role.

It demonstrates:

- Testing **non-deterministic chatbot outputs** without checking exact wording
- Using a **golden dataset** of pharmacy-style test cases
- Validating **intent + business outcome**
- Checking healthcare/pharmacy **guardrails**
- Catching unsafe answers such as medication advice or controlled-substance bypass requests
- Computing simple teaching versions of **BLEU, ROUGE, METEOR, and BERTScore-style** metrics
- Running a **regression gate** with pytest
- Reviewing Python interview basics: negative indexing, slicing, if/runtime error confidence

> Important: this project is intentionally lightweight. The metric implementations are simplified teaching versions, not official production BLEU/ROUGE/METEOR/BERTScore packages.

## How to run

From this folder:

```bash
python -m pytest -q
PYTHONPATH=src python -m ai_chatbot_qa_demo.report --golden data/golden_pharmacy_cases.json --out reports/latest_report.md
```

If running from outside this folder:

```bash
cd ~/ai-chatbot-testing-demo
python -m pytest -q
PYTHONPATH=src python -m ai_chatbot_qa_demo.report --golden data/golden_pharmacy_cases.json --out reports/latest_report.md
```

## How to study this project

Read in this order:

1. `data/golden_pharmacy_cases.json` — examples of real AI QA test cases
2. `tests/test_chatbot_evaluation.py` — how to test non-deterministic output correctly
3. `src/ai_chatbot_qa_demo/evaluator.py` — validation logic for intent, outcome, concepts, and guardrails
4. `src/ai_chatbot_qa_demo/chatbot.py` — toy chatbot with varied wording
5. `tests/test_regression_gate.py` — how release threshold checks work
6. `tests/test_metrics.py` — BLEU/ROUGE/METEOR/BERTScore memory cheat in code
7. `tests/test_python_trace_basics.py` — Python interview trace basics

## Core lesson

For chatbot testing, do **not** assert exact text like this:

```python
assert response.text == "I can help start a refill request."
```

Instead test stable behavior:

```python
assert response.intent == "refill_request"
assert response.business_outcome == "starts_refill_workflow"
assert evaluator_result.passed
```

This is the same concept from your interview: validate **intent + business outcome + guardrails**, not exact wording.
