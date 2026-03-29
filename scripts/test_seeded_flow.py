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
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    import httpx
except ImportError:
    print("❌ httpx not installed. Run: pip install httpx")
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


# =============================================================================
# Utility Functions
# =============================================================================


def load_payloads() -> dict[str, Any]:
    """Load test payloads from JSON file."""
    if not PAYLOADS_FILE.exists():
        print(f"{RED}✗ Payloads file not found: {PAYLOADS_FILE}{RESET}")
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
        print(f"  {GREEN}✓{RESET} {test_name}")
    else:
        print(f"  {RED}✗{RESET} {test_name}")
    if details:
        print(f"    {YELLOW}→ {details}{RESET}")


# =============================================================================
# Setup Functions
# =============================================================================


def ensure_camera_exists(client: httpx.Client, verbose: bool = False) -> bool:
    """Ensure test camera exists in the system."""
    camera_data = {
        "id": TEST_CAMERA_ID,
        "name": "Demo Test Camera",
        "location": "Test Gate Entry",
        "rtsp_url": "rtsp://localhost:8554/test",
        "direction": "in",
        "is_active": True,
    }

    try:
        # Try to get existing camera
        res = client.get(f"/api/v1/cameras/{TEST_CAMERA_ID}")
        if res.status_code == 200:
            if verbose:
                print(f"  {GREEN}✓{RESET} Camera already exists")
            return True
    except httpx.RequestError:
        pass

    # Try to create camera
    try:
        res = client.post("/api/v1/cameras", json=camera_data)
        if res.status_code in (200, 201):
            if verbose:
                print(f"  {GREEN}✓{RESET} Camera created successfully")
            return True
        elif res.status_code == 409:  # Conflict - already exists
            if verbose:
                print(f"  {GREEN}✓{RESET} Camera already exists (conflict)")
            return True
        else:
            if verbose:
                print(f"  {YELLOW}⚠{RESET} Camera creation returned {res.status_code}")
            # Continue anyway - camera might not be required for events endpoint
            return True
    except httpx.RequestError as e:
        print(f"  {RED}✗{RESET} Failed to setup camera: {e}")
        return False


def ensure_registered_account(
    client: httpx.Client,
    plate_text: str,
    balance: int = 100000,
    verbose: bool = False,
) -> bool:
    """Ensure a registered account exists for testing."""
    # First check if account exists
    try:
        res = client.get(f"/api/v1/accounts/{plate_text}")
        if res.status_code == 200:
            account = res.json()
            if account.get("registration_status") == "registered":
                if verbose:
                    print(f"  {GREEN}✓{RESET} Registered account exists: {plate_text}")
                return True
    except httpx.RequestError:
        pass

    # Try to create/update account via admin endpoint (if available)
    account_data = {
        "plate_text": plate_text,
        "balance_vnd": balance,
        "registration_status": "registered",
    }

    try:
        # Try PUT first (update or create)
        res = client.put(f"/api/v1/accounts/{plate_text}", json=account_data)
        if res.status_code in (200, 201):
            if verbose:
                print(f"  {GREEN}✓{RESET} Registered account created: {plate_text}")
            return True
    except httpx.RequestError:
        pass

    try:
        # Try POST to accounts endpoint
        res = client.post("/api/v1/accounts", json=account_data)
        if res.status_code in (200, 201):
            if verbose:
                print(f"  {GREEN}✓{RESET} Registered account created: {plate_text}")
            return True
    except httpx.RequestError:
        pass

    if verbose:
        print(f"  {YELLOW}⚠{RESET} Could not pre-create registered account: {plate_text}")
        print(f"      Test may fail or create temporary_registered instead")

    return False


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
    payload["timestamp"] = datetime.utcnow().isoformat()

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
            print(f"{RED}✗ Test '{only_test}' not found{RESET}")
            return 0, 1

    passed = 0
    failed = 0

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        # Health check
        print_header("Connectivity Check")
        try:
            res = client.get("/health")
            if res.status_code == 200:
                print(f"  {GREEN}✓{RESET} Backend is healthy at {base_url}")
            else:
                print(f"  {YELLOW}⚠{RESET} Health check returned {res.status_code}")
        except httpx.RequestError as e:
            print(f"  {RED}✗{RESET} Cannot connect to {base_url}: {e}")
            print(f"\n{RED}Make sure the backend is running!{RESET}")
            print(f"  → cd apps/backend && uvicorn app.main:app --reload")
            return 0, len(test_cases)

        # Setup phase
        print_header("Setup Phase")
        ensure_camera_exists(client, verbose=True)

        # Pre-create registered account for first two tests
        for tc in test_cases:
            setup = tc.get("setup_required")
            if setup and setup.get("create_registered_account"):
                ensure_registered_account(
                    client,
                    plate_text=setup["plate_text"],
                    balance=setup.get("initial_balance", 100000),
                    verbose=True,
                )

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
                    print(f"    {GREEN}✓ PASSED{RESET}")
                else:
                    print(f"    {RED}✗ FAILED: {details}{RESET}")

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
        print(f"\n{GREEN}{BOLD}✓ All tests passed!{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{RED}{BOLD}✗ {failed} test(s) failed{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
