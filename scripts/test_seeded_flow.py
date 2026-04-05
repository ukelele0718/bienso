#!/usr/bin/env python3
"""
Test Seeded Mode Flow - API Integration Tests

This script tests the barrier decision logic for seeded mode by sending
real HTTP requests to the backend API and verifying the responses.

Usage:
    python test_seeded_flow.py
    python test_seeded_flow.py --base-url http://localhost:8001
    python test_seeded_flow.py --verbose
    python test_seeded_flow.py --only test_registered_in
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    import httpx
except ImportError:
    print("[ERROR] httpx not installed. Run: pip install httpx")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_BASE_URL = "http://localhost:8000"
PAYLOADS_FILE = Path(__file__).parent / "demo_payloads.json"
TEST_CAMERA_ID = "11111111-1111-1111-1111-111111111111"

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

OK_MARK = "[OK]"
FAIL_MARK = "[FAIL]"
WARN_MARK = "[WARN]"


# =============================================================================
# Utility Functions
# =============================================================================


def load_payloads() -> dict[str, Any]:
    """Load test payloads from JSON file."""
    if not PAYLOADS_FILE.exists():
        print(f"{RED}{FAIL_MARK} Payloads file not found: {PAYLOADS_FILE}{RESET}")
        sys.exit(1)

    with open(PAYLOADS_FILE) as f:
        return json.load(f)


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_result(test_name: str, passed: bool, details: str = "") -> None:
    """Print test result with ✓ or ✗."""
    if passed:
        print(f"  {GREEN}{OK_MARK}{RESET} {test_name}")
    else:
        print(f"  {RED}{FAIL_MARK}{RESET} {test_name}")
    if details:
        print(f"    {YELLOW}→ {details}{RESET}")


# =============================================================================
# Setup Functions
# =============================================================================


def ensure_camera_exists(client: httpx.Client, verbose: bool = False) -> bool:
    """Ensure test camera exists in the database for event FK."""
    # Current backend does not expose camera endpoints.
    # Assume migration/seed already contains the test camera used in payloads.
    if verbose:
        print(f"  {YELLOW}{WARN_MARK}{RESET} Camera API not available, using pre-seeded camera id")
    return True


def pick_registered_plate(client: httpx.Client, verbose: bool = False) -> str | None:
    """Get one registered plate from backend for deterministic registered-flow tests."""
    try:
        res = client.get(
            "/api/v1/accounts",
            params={"registration_status": "registered", "page": 1, "page_size": 1},
        )
        if res.status_code != 200:
            return None

        body = res.json()
        items = body.get("items") or []
        if not items:
            return None

        plate_text = items[0].get("plate_text")
        if verbose and plate_text:
            print(f"  {GREEN}{OK_MARK}{RESET} Using registered plate from DB: {plate_text}")
        return plate_text
    except httpx.RequestError:
        return None


# =============================================================================
# Test Runner
# =============================================================================


def run_test(
    client: httpx.Client,
    test_case: dict[str, Any],
    verbose: bool = False,
) -> tuple[bool, str]:
    """
    Run a single test case.

    Returns:
        Tuple of (passed, details_message)
    """
    payload = test_case["payload"].copy()
    expected = test_case["expected"]

    # Add timestamp to payload
    payload["timestamp"] = datetime.now(UTC).isoformat()

    # Make unique track_id for each run
    base_track_id = payload.get("track_id", "track")
    payload["track_id"] = f"{base_track_id}-{uuid4().hex[:8]}"

    if verbose:
        print(f"    Sending: plate={payload['plate_text']}, dir={payload['direction']}")

    try:
        res = client.post("/api/v1/events", json=payload)
    except httpx.RequestError as e:
        return False, f"Request failed: {e}"

    # Check status code
    if res.status_code != expected.get("status_code", 200):
        return False, f"Status {res.status_code}, expected {expected.get('status_code', 200)}"

    body = res.json()

    # Check expected fields
    mismatches = []
    for key, expected_value in expected.items():
        if key == "status_code":
            continue  # Already checked

        actual_value = body.get(key)
        if actual_value != expected_value:
            mismatches.append(f"{key}: got '{actual_value}', expected '{expected_value}'")

    if mismatches:
        return False, "; ".join(mismatches)

    if verbose:
        print(f"    Response: action={body.get('barrier_action')}, "
              f"status={body.get('registration_status')}, "
              f"verify={body.get('needs_verification')}")

    return True, ""


def run_all_tests(
    base_url: str,
    verbose: bool = False,
    only_test: str | None = None,
) -> tuple[int, int]:
    """
    Run all test cases from payloads file.

    Returns:
        Tuple of (passed_count, failed_count)
    """
    payloads = load_payloads()
    test_cases = payloads.get("test_cases", [])

    if only_test:
        test_cases = [tc for tc in test_cases if tc["id"] == only_test]
        if not test_cases:
            print(f"{RED}{FAIL_MARK} Test '{only_test}' not found{RESET}")
            return 0, 1

    passed = 0
    failed = 0

    with httpx.Client(base_url=base_url, timeout=30.0, trust_env=False) as client:
        # Health check
        print_header("Connectivity Check")
        try:
            res = client.get("/health")
            if res.status_code == 200:
                print(f"  {GREEN}{OK_MARK}{RESET} Backend is healthy at {base_url}")
            else:
                print(f"  {YELLOW}{WARN_MARK}{RESET} Health check returned {res.status_code}")
        except httpx.RequestError as e:
            print(f"  {RED}{FAIL_MARK}{RESET} Cannot connect to {base_url}: {e}")
            print(f"\n{RED}Make sure the backend is running!{RESET}")
            print(f"  → cd apps/backend && uvicorn app.main:app --reload")
            return 0, len(test_cases)

        # Setup phase
        print_header("Setup Phase")
        ensure_camera_exists(client, verbose=True)

        # Ensure registered-flow tests use a real registered plate from DB
        registered_plate = pick_registered_plate(client, verbose=True)
        if registered_plate:
            for tc in test_cases:
                if tc.get("id") in {"test_registered_in", "test_registered_out"}:
                    if "payload" in tc:
                        tc["payload"]["plate_text"] = registered_plate
        else:
            print(f"  {YELLOW}{WARN_MARK}{RESET} No registered plate found in DB for registered-flow tests")

        # Make dynamic fixture plates to avoid payload-state collision across repeated runs
        unknown_motorbike_plate = f"UNK{uuid4().hex[:6].upper()}"
        unknown_car_plate = f"CAR{uuid4().hex[:6].upper()}"

        for tc in test_cases:
            if tc.get("id") in {"test_unknown_in", "test_temporary_out"} and "payload" in tc:
                tc["payload"]["plate_text"] = unknown_motorbike_plate

        if not only_test and payloads.get("additional_scenarios"):
            for scenario in payloads["additional_scenarios"]:
                if scenario.get("id") == "test_low_confidence":
                    scenario_payload = scenario.get("payload", {})
                    scenario_payload["plate_text"] = f"LOW{uuid4().hex[:6].upper()}"
                    scenario["payload"] = scenario_payload
                if scenario.get("id") == "test_car_vehicle_type":
                    scenario_payload = scenario.get("payload", {})
                    scenario_payload["plate_text"] = unknown_car_plate
                    scenario["payload"] = scenario_payload

        # Run tests
        print_header("Running Test Cases")

        for test_case in test_cases:
            test_id = test_case["id"]
            test_name = test_case["name"]

            if verbose:
                print(f"\n  {BOLD}[{test_id}]{RESET} {test_name}")
                print(f"    {test_case.get('description', '')}")

            success, details = run_test(client, test_case, verbose)

            if not verbose:
                print_result(f"[{test_id}] {test_name}", success, details)
            else:
                if success:
                    print(f"    {GREEN}{OK_MARK} PASSED{RESET}")
                else:
                    print(f"    {RED}{FAIL_MARK} FAILED: {details}{RESET}")

            if success:
                passed += 1
            else:
                failed += 1

        # Run additional scenarios if not filtering
        if not only_test and payloads.get("additional_scenarios"):
            print_header("Additional Scenarios")
            for scenario in payloads["additional_scenarios"]:
                test_id = scenario["id"]
                test_name = scenario["name"]

                success, details = run_test(client, scenario, verbose)
                print_result(f"[{test_id}] {test_name}", success, details)

                if success:
                    passed += 1
                else:
                    failed += 1

    return passed, failed


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test seeded mode flow against backend API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_seeded_flow.py                          # Run all tests
  python test_seeded_flow.py --verbose                # Run with detailed output
  python test_seeded_flow.py --base-url http://localhost:8001
  python test_seeded_flow.py --only test_registered_in
        """,
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Backend API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed test output",
    )
    parser.add_argument(
        "--only",
        metavar="TEST_ID",
        help="Run only the specified test (e.g., test_registered_in)",
    )

    args = parser.parse_args()

    print(f"\n{BOLD}Seeded Mode Flow Test Suite{RESET}")
    print(f"Target: {args.base_url}")
    print(f"Payloads: {PAYLOADS_FILE}")

    passed, failed = run_all_tests(
        base_url=args.base_url,
        verbose=args.verbose,
        only_test=args.only,
    )

    # Summary
    total = passed + failed
    print_header("Summary")
    print(f"  Total:  {total}")
    print(f"  {GREEN}Passed: {passed}{RESET}")
    print(f"  {RED}Failed: {failed}{RESET}")

    if failed == 0:
        print(f"\n{GREEN}{BOLD}{OK_MARK} All tests passed!{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{RED}{BOLD}{FAIL_MARK} {failed} test(s) failed{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
