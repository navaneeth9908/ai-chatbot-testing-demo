from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .chatbot import ToyPharmacyChatbot
from .data_validation import load_golden_cases
from .evaluator import evaluate_dataset, regression_gate


def build_report(cases: list[dict[str, Any]], results: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        "# AI Chatbot QA Evaluation Report",
        "",
        f"Overall gate: {'PASS' if summary['passed'] else 'FAIL'}",
        f"Pass rate: {summary['pass_rate']:.1%}",
        f"Threshold: {summary['minimum_pass_rate']:.1%}",
        f"Cases passed: {summary['passed_cases']} / {summary['total_cases']}",
        "",
        "## Case Results",
        "",
    ]

    case_by_id = {case["id"]: case for case in cases}
    for result in results:
        case = case_by_id[result["case_id"]]
        lines.extend(
            [
                f"### {result['case_id']} — {case.get('area', 'unknown area')}",
                f"Status: {'PASS' if result['passed'] else 'FAIL'}",
                f"User message: {case['user_message']}",
                f"Expected intent: `{case['expected_intent']}`",
                f"Actual intent: `{result['intent']}`",
                f"Expected business outcome: `{case['expected_business_outcome']}`",
                f"Actual business outcome: `{result['business_outcome']}`",
                f"Response: {result['response_text']}",
            ]
        )
        if result["failures"]:
            lines.append("Failures:")
            lines.extend(f"- {failure}" for failure in result["failures"])
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run toy AI/chatbot QA evaluation")
    parser.add_argument("--golden", default="data/golden_pharmacy_cases.json", help="Path to golden dataset JSON")
    parser.add_argument("--out", default="reports/latest_report.md", help="Output report path (.md or .json)")
    parser.add_argument("--threshold", type=float, default=0.85, help="Minimum pass rate required")
    parser.add_argument("--seed", type=int, default=11, help="Random seed for stable demo output")
    args = parser.parse_args(argv)

    cases = load_golden_cases(args.golden)
    chatbot = ToyPharmacyChatbot(seed=args.seed)
    results = evaluate_dataset(cases, chatbot.ask)
    summary = regression_gate(results, minimum_pass_rate=args.threshold)

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.suffix.lower() == ".json":
        output_path.write_text(json.dumps({"summary": summary, "results": results}, indent=2), encoding="utf-8")
    else:
        output_path.write_text(build_report(cases, results, summary), encoding="utf-8")

    print(f"Report written to: {output_path}")
    print(f"Gate: {'PASS' if summary['passed'] else 'FAIL'} | Pass rate: {summary['pass_rate']:.1%}")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
