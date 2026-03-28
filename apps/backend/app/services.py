from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BarrierDecision:
    registration_status: str
    barrier_action: str
    barrier_reason: str
    needs_verification: bool


def decide_barrier(registration_status: str, direction: str) -> BarrierDecision:
    if registration_status == "registered" and direction == "in":
        return BarrierDecision(
            registration_status=registration_status,
            barrier_action="open",
            barrier_reason="registered_vehicle_in",
            needs_verification=False,
        )
    if registration_status == "temporary_registered" and direction == "in":
        return BarrierDecision(
            registration_status=registration_status,
            barrier_action="open",
            barrier_reason="unknown_vehicle_auto_temporary_register",
            needs_verification=False,
        )
    if registration_status == "temporary_registered" and direction == "out":
        return BarrierDecision(
            registration_status=registration_status,
            barrier_action="hold",
            barrier_reason="temporary_vehicle_out_requires_verify",
            needs_verification=True,
        )
    if registration_status == "unknown" and direction == "in":
        return BarrierDecision(
            registration_status="temporary_registered",
            barrier_action="open",
            barrier_reason="unknown_vehicle_auto_temporary_register",
            needs_verification=False,
        )
    return BarrierDecision(
        registration_status=registration_status,
        barrier_action="hold",
        barrier_reason="default_hold",
        needs_verification=True,
    )
