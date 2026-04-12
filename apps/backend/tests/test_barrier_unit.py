"""Unit tests for barrier decision rules (all branches of decide_barrier)."""
from __future__ import annotations

from app.services import decide_barrier


# --- registered ---

def test_registered_vehicle_in_open() -> None:
    decision = decide_barrier("registered", "in")
    assert decision.barrier_action == "open"
    assert decision.barrier_reason == "registered_vehicle_in"
    assert decision.needs_verification is False


def test_registered_vehicle_out_open() -> None:
    decision = decide_barrier("registered", "out")
    assert decision.barrier_action == "open"
    assert decision.barrier_reason == "registered_vehicle_out"
    assert decision.needs_verification is False


# --- temporary_registered ---

def test_temporary_vehicle_in_open() -> None:
    decision = decide_barrier("temporary_registered", "in")
    assert decision.barrier_action == "open"
    assert decision.barrier_reason == "unknown_vehicle_auto_temporary_register"
    assert decision.needs_verification is False


def test_temporary_vehicle_out_hold_and_verify() -> None:
    decision = decide_barrier("temporary_registered", "out")
    assert decision.barrier_action == "hold"
    assert decision.barrier_reason == "temporary_vehicle_out_requires_verify"
    assert decision.needs_verification is True


# --- unknown ---

def test_unknown_in_promotes_to_temporary_and_opens() -> None:
    decision = decide_barrier("unknown", "in")
    assert decision.registration_status == "temporary_registered"
    assert decision.barrier_action == "open"
    assert decision.barrier_reason == "unknown_vehicle_auto_temporary_register"
    assert decision.needs_verification is False


def test_unknown_out_hold() -> None:
    decision = decide_barrier("unknown", "out")
    assert decision.barrier_action == "hold"
    assert decision.barrier_reason == "default_hold"
    assert decision.needs_verification is True


# --- default / edge cases ---

def test_invalid_status_defaults_to_hold() -> None:
    decision = decide_barrier("invalid_status", "in")
    assert decision.barrier_action == "hold"
    assert decision.barrier_reason == "default_hold"
    assert decision.needs_verification is True


def test_reason_values_are_nonempty_strings() -> None:
    """All branches return a non-empty reason string."""
    cases = [
        ("registered", "in"),
        ("registered", "out"),
        ("temporary_registered", "in"),
        ("temporary_registered", "out"),
        ("unknown", "in"),
        ("unknown", "out"),
    ]
    for status, direction in cases:
        decision = decide_barrier(status, direction)
        assert isinstance(decision.barrier_reason, str)
        assert len(decision.barrier_reason) > 0, f"Empty reason for {status}/{direction}"
