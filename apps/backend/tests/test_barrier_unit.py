from __future__ import annotations

"""Template unit tests for barrier decision logic.

Team QA: fill expected values according to finalized barrier rules,
then remove `pytest.skip(...)` lines.
"""

from dataclasses import dataclass

import pytest


@dataclass
class BarrierDecision:
    barrier_action: str
    barrier_reason: str
    needs_verification: bool


def decide_barrier_action(registration_status: str, direction: str) -> BarrierDecision:
    """Temporary local stub for unit-test scaffolding.

    Replace this stub by importing real decision function from app service layer,
    for example:
      from app.services.barrier import decide_barrier_action
    """
    if registration_status == "registered" and direction == "in":
        return BarrierDecision("open", "registered_vehicle_in", False)
    if registration_status == "temporary_registered" and direction == "in":
        return BarrierDecision("open", "temporary_registered_vehicle_in", False)
    if registration_status == "temporary_registered" and direction == "out":
        return BarrierDecision("hold", "temporary_vehicle_out_requires_verify", True)
    return BarrierDecision("hold", "unknown_rule", True)


@pytest.mark.unit
def test_registered_vehicle_in_open() -> None:
    decision = decide_barrier_action("registered", "in")
    assert decision.barrier_action == "open"
    assert decision.needs_verification is False


@pytest.mark.unit
def test_temporary_vehicle_in_open() -> None:
    decision = decide_barrier_action("temporary_registered", "in")
    assert decision.barrier_action == "open"
    assert decision.needs_verification is False


@pytest.mark.unit
def test_temporary_vehicle_out_hold_and_verify() -> None:
    decision = decide_barrier_action("temporary_registered", "out")
    assert decision.barrier_action == "hold"
    assert decision.needs_verification is True


@pytest.mark.unit
def test_unknown_out_hold() -> None:
    decision = decide_barrier_action("unknown", "out")
    assert decision.barrier_action == "hold"


@pytest.mark.unit
def test_reason_values_follow_contract() -> None:
    decision = decide_barrier_action("temporary_registered", "out")
    assert isinstance(decision.barrier_reason, str)
    assert len(decision.barrier_reason) > 0


@pytest.mark.unit
def test_verify_success_transition_template() -> None:
    pytest.skip("TODO: wire real verify function and assert transition hold -> open")


@pytest.mark.unit
def test_verify_fail_stays_hold_template() -> None:
    pytest.skip("TODO: wire real verify function and assert hold remains on verify fail")
