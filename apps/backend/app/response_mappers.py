from __future__ import annotations

# mypy: disable-error-code="arg-type"
# Reason: SQLAlchemy Mapped[str] -> Pydantic Literal[...] narrowing;
# values are validated at runtime by Pydantic.

from .models import Account, BarrierAction, PlateRead, VehicleEvent
from .schemas import AccountOut, BarrierActionOut, EventOut


def to_event_out(event: VehicleEvent, plate_read: PlateRead | None, barrier_action: BarrierAction | None) -> EventOut:
    return EventOut(
        id=str(event.id),
        camera_id=str(event.camera_id),
        timestamp=event.timestamp,
        direction=event.direction,
        vehicle_type=event.vehicle_type,
        track_id=event.track_id,
        plate_text=plate_read.plate_text if plate_read else None,
        confidence=plate_read.confidence if plate_read else None,
        snapshot_url=plate_read.snapshot_url if plate_read else None,
        registration_status=barrier_action.registration_status if barrier_action else None,
        barrier_action=barrier_action.barrier_action if barrier_action else None,
        barrier_reason=barrier_action.barrier_reason if barrier_action else None,
        needs_verification=barrier_action.needs_verification if barrier_action else None,
    )


def to_barrier_action_out(row: BarrierAction) -> BarrierActionOut:
    return BarrierActionOut(
        id=row.id,
        event_id=row.event_id,
        plate_text=row.plate_text,
        registration_status=row.registration_status,
        barrier_action=row.barrier_action,
        barrier_reason=row.barrier_reason,
        needs_verification=row.needs_verification,
        verified_by=row.verified_by,
        verified_at=row.verified_at,
        created_at=row.created_at,
    )


def to_account_out(row: Account) -> AccountOut:
    return AccountOut(
        plate_text=row.plate_text,
        balance_vnd=row.balance_vnd,
        registration_status=row.registration_status,
    )
