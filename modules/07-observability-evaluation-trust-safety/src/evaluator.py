"""Offline evaluator harness for insurance triage routing.

The default mode is model-free and deterministic so learners and CI can run it without any live
Azure dependency. An optional ``--live`` mode exists only for explicit experimentation with a
user-supplied router function.
"""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Callable

DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[1] / "eval" / "triage-eval-dataset.json"
MODULE_ROOT = Path(__file__).resolve().parents[1]
VALID_ROUTES = {"auto-adjudicate", "manual-review", "fraud-escalation"}

FRAUD_KEYWORDS = (
    "staged",
    "arson",
    "forged",
    "altered receipt",
    "altered receipts",
    "duplicate repair bill",
    "synthetic invoice",
    "multiple prior claims",
    "inconsistent story",
    "changed the story",
    "suspicious",
    "cash only",
)

MANUAL_REVIEW_KEYWORDS = (
    "third party",
    "liability dispute",
    "injury",
    "unclear",
    "police report pending",
    "police report",
    "missing documents",
    "missing documentation",
    "coverage unclear",
    "shared fault",
    "commercial use",
    "witness disagreement",
)


def load_eval_dataset(dataset_path: str | Path) -> list[dict[str, Any]]:
    """Load and minimally validate the evaluation dataset."""
    path = Path(dataset_path)
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("Evaluation dataset must be a JSON array of cases.")

    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Case #{index} must be an object.")
        if not case.get("id"):
            raise ValueError(f"Case #{index} is missing 'id'.")
        if not case.get("test_case_description"):
            raise ValueError(f"Case '{case.get('id', index)}' is missing 'test_case_description'.")
        input_block = case.get("input") or {}
        expected_block = case.get("expected") or {}
        if not input_block.get("fnol_narrative"):
            raise ValueError(f"Case '{case['id']}' is missing input.fnol_narrative.")
        route = expected_block.get("route")
        if route not in VALID_ROUTES:
            raise ValueError(f"Case '{case['id']}' has invalid expected.route '{route}'.")

    return cases


def classify_fnol_narrative(fnol_narrative: str) -> str:
    """Route a narrative with deterministic keyword rules."""
    narrative = fnol_narrative.lower()

    if any(keyword in narrative for keyword in FRAUD_KEYWORDS):
        return "fraud-escalation"

    if any(keyword in narrative for keyword in MANUAL_REVIEW_KEYWORDS):
        return "manual-review"

    return "auto-adjudicate"


def default_router(case: dict[str, Any]) -> dict[str, Any]:
    """Default offline router used by the module and CI."""
    narrative = case["input"]["fnol_narrative"]
    route = classify_fnol_narrative(narrative)
    return {
        "route": route,
        "reason": "keyword-routing",
    }


def normalize_router_result(result: Any) -> dict[str, Any]:
    if isinstance(result, str):
        return {"route": result}
    if isinstance(result, dict) and isinstance(result.get("route"), str):
        return result
    raise TypeError("Router function must return a route string or a dict containing 'route'.")


def score_cases(
    cases: list[dict[str, Any]],
    router_fn: Callable[[dict[str, Any]], Any] | None = None,
) -> dict[str, Any]:
    """Run routing predictions and build a scorecard."""
    router = router_fn or default_router
    per_case: list[dict[str, Any]] = []
    passed = 0

    for case in cases:
        expected_route = case["expected"]["route"]
        actual = normalize_router_result(router(case))
        actual_route = actual["route"]
        is_pass = actual_route == expected_route
        passed += int(is_pass)
        per_case.append(
            {
                "id": case["id"],
                "test_case_description": case["test_case_description"],
                "expected_route": expected_route,
                "actual_route": actual_route,
                "passed": is_pass,
                "tags": case.get("tags", []),
                "reason": actual.get("reason", ""),
            }
        )

    total = len(cases)
    failed = total - passed
    pass_rate = (passed / total) if total else 0.0
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "per_case": per_case,
    }


def run_evaluation(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    router_fn: Callable[[dict[str, Any]], Any] | None = None,
    live_mode: bool = False,
) -> dict[str, Any]:
    """Load the dataset and run the selected router."""
    if live_mode and router_fn is None:
        raise ValueError("Live mode requires an explicit router function.")

    cases = load_eval_dataset(dataset_path)
    scorecard = score_cases(cases, router_fn=router_fn)
    scorecard["mode"] = "live" if live_mode else "offline"
    scorecard["dataset_path"] = display_dataset_path(dataset_path)
    return scorecard


def load_router(reference: str) -> Callable[[dict[str, Any]], Any]:
    """Import a router callable from ``module:function`` syntax."""
    if ":" not in reference:
        raise ValueError("Router reference must use the form module:function.")

    module_name, function_name = reference.split(":", 1)
    module = importlib.import_module(module_name)
    router_fn = getattr(module, function_name)
    if not callable(router_fn):
        raise TypeError(f"Router reference '{reference}' is not callable.")
    return router_fn


def write_scorecard(scorecard: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")


def display_dataset_path(dataset_path: str | Path) -> str:
    """Return a sanitized dataset path for console and scorecard output."""
    path = Path(dataset_path).resolve()
    try:
        return str(path.relative_to(MODULE_ROOT))
    except ValueError:
        return path.name


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the offline triage evaluator.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH), help="Path to the evaluation dataset JSON file.")
    parser.add_argument("--output", help="Optional path to write the scorecard JSON.")
    parser.add_argument("--threshold", type=float, help="Optional minimum pass rate (0-1). Returns exit code 1 when missed.")
    parser.add_argument("--router", help="Optional router callable in module:function form.")
    parser.add_argument("--live", action="store_true", help="Opt-in live mode. Requires --router.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    router_fn = load_router(args.router) if args.router else None
    scorecard = run_evaluation(args.dataset, router_fn=router_fn, live_mode=args.live)

    if args.output:
        write_scorecard(scorecard, args.output)

    print(f"Mode:     {scorecard['mode']}")
    print(f"Dataset:  {scorecard['dataset_path']}")
    print(f"Total:    {scorecard['total']}")
    print(f"Passed:   {scorecard['passed']}")
    print(f"Failed:   {scorecard['failed']}")
    print(f"PassRate: {scorecard['pass_rate']:.2%}")

    if args.threshold is not None and scorecard["pass_rate"] < args.threshold:
        print(f"Threshold not met: required {args.threshold:.2%}.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
