#!/usr/bin/env python3
"""
Evaluation runner for Resume Screener

Tests the scoring function against predefined test cases.
Run with: python run_evaluations.py
"""

import httpx
import yaml
import json
from pathlib import Path

SCORING_ENDPOINT = "https://faas-nyc1-2ef2e6cc.doserverless.co/api/v1/web/fn-309f9b5b-dd19-493d-8450-b30f94517e21/default/resume-screener"


def load_evaluations(filepath: str = "evaluations.yaml") -> dict:
    """Load evaluation test cases."""
    with open(filepath) as f:
        return yaml.safe_load(f)


def run_test_case(test_case: dict) -> dict:
    """Run a single test case and return results."""
    name = test_case.get("name")
    input_data = test_case.get("input")
    expected_score_range = test_case.get("expected_score_range", [0, 100])
    expected_recommendation = test_case.get("expected_recommendation", "")

    print(f"\n📝 Test: {name}")
    print(f"   {test_case.get('description', '')}")

    try:
        response = httpx.post(
            SCORING_ENDPOINT,
            json=input_data,
            timeout=10
        )
        # Response is already the result (not nested in body)
        result = response.json()

        if result.get("error"):
            return {
                "name": name,
                "status": "FAILED",
                "error": result["error"],
                "result": None
            }

        # Check score in range
        score = result.get("score", 0)
        score_in_range = expected_score_range[0] <= score <= expected_score_range[1]

        # Check recommendation
        recommendation = result.get("recommendation", "")
        recommendation_match = expected_recommendation in recommendation if expected_recommendation else True

        # Determine pass/fail
        passed = score_in_range and recommendation_match
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"   {status}")
        print(f"   Score: {score}/100 (expected: {expected_score_range[0]}-{expected_score_range[1]})")
        print(f"   Recommendation: {recommendation[:60]}...")
        if not score_in_range:
            print(f"   ⚠️  Score out of range!")
        if not recommendation_match:
            print(f"   ⚠️  Recommendation doesn't match expected: {expected_recommendation}")

        return {
            "name": name,
            "status": "PASSED" if passed else "FAILED",
            "score": score,
            "score_in_range": score_in_range,
            "recommendation": recommendation[:100],
            "recommendation_match": recommendation_match,
            "result": result
        }

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return {
            "name": name,
            "status": "ERROR",
            "error": str(e),
            "result": None
        }


def main():
    """Run all evaluations."""
    print("🎯 Resume Screener Evaluation Suite")
    print("=" * 70)

    evals = load_evaluations()
    test_cases = evals.get("test_cases", [])

    print(f"\n📊 Running {len(test_cases)} test cases...\n")

    results = []
    for test_case in test_cases:
        result = run_test_case(test_case)
        results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print(f"\n✅ Passed: {passed}/{len(test_cases)}")
    print(f"❌ Failed: {failed}/{len(test_cases)}")
    print(f"⚠️  Errors: {errors}/{len(test_cases)}")

    if failed > 0:
        print("\n🔍 Failed tests:")
        for result in results:
            if result["status"] == "FAILED":
                print(f"   - {result['name']}")

    # Save detailed results
    results_file = Path("evaluation_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📁 Detailed results saved to: {results_file}")

    # Exit code
    return 0 if failed == 0 and errors == 0 else 1


if __name__ == "__main__":
    exit(main())
