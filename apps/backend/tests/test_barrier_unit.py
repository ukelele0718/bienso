from __future__ import annotations

from app.services import decide_barrier


def test_registered_vehicle_in_open() -> None:
    decision = decide_barrier("registered", "in")
    assert decision.barrier_action == "open"
    assert decision.needs_verification is False


def test_temporary_vehicle_in_open() -> None:
    decision = decide_barrier("temporary_registered", "in")
    assert decision.barrier_action == "open"
    assert decision.needs_verification is False


def test_temporary_vehicle_out_hold_and_verify() -> None:
    decision = decide_barrier("temporary_registered", "out")
    assert decision.barrier_action == "hold"
    assert decision.needs_verification is True


def test_unknown_out_hold() -> None:
    decision = decide_barrier("unknown", "out")
    assert decision.barrier_action == "hold"


def test_reason_values_follow_contract() -> None:
    decision = decide_barrier("temporary_registered", "out")
    assert isinstance(decision.barrier_reason, str)
    assert len(decision.barrier_reason) > 0
