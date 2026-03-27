from __future__ import annotations

from datetime import datetime
from typing import Iterable
from uuid import uuid4

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from .config import settings
from .models import Account, PlateRead, Transaction, VehicleEvent


class NotFoundError(Exception):
    pass


def create_event(db: Session, payload: dict) -> VehicleEvent:
    event = VehicleEvent(
        id=str(uuid4()),
        camera_id=payload["camera_id"],
        timestamp=payload["timestamp"],
        direction=payload["direction"],
        vehicle_type=payload["vehicle_type"],
        track_id=payload["track_id"],
    )
    db.add(event)
    db.flush()

    plate_text = payload.get("plate_text")
    plate_read = PlateRead(
        id=str(uuid4()),
        event_id=event.id,
        plate_text=plate_text,
        confidence=payload.get("confidence"),
        snapshot_url=payload.get("snapshot_url"),
        crop_url=None,
        ocr_status="success" if plate_text else "failed",
    )
    db.add(plate_read)

    if plate_text:
        account = db.execute(select(Account).where(Account.plate_text == plate_text)).scalar_one_or_none()
        if account is None:
            account = Account(
                id=str(uuid4()),
                plate_text=plate_text,
                balance_vnd=settings.initial_balance_vnd,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(account)
            db.flush()
            db.add(
                Transaction(
                    id=str(uuid4()),
                    account_id=account.id,
                    event_id=None,
                    amount_vnd=settings.initial_balance_vnd,
                    balance_after_vnd=settings.initial_balance_vnd,
                    type="init",
                    created_at=payload["timestamp"],
                )
            )

        account.balance_vnd -= settings.charge_per_event_vnd
        account.updated_at = datetime.utcnow()
        db.add(
            Transaction(
                id=str(uuid4()),
                account_id=account.id,
                event_id=event.id,
                amount_vnd=-settings.charge_per_event_vnd,
                balance_after_vnd=account.balance_vnd,
                type="event_charge",
                created_at=payload["timestamp"],
            )
        )

    db.commit()
    db.refresh(event)
    return event


def list_events(
    db: Session,
    plate: str | None,
    from_time: datetime | None,
    to_time: datetime | None,
    direction: str | None,
    vehicle_type: str | None,
) -> list[VehicleEvent]:
    stmt = select(VehicleEvent)
    if from_time:
        stmt = stmt.where(VehicleEvent.timestamp >= from_time)
    if to_time:
        stmt = stmt.where(VehicleEvent.timestamp <= to_time)
    if direction:
        stmt = stmt.where(VehicleEvent.direction == direction)
    if vehicle_type:
        stmt = stmt.where(VehicleEvent.vehicle_type == vehicle_type)
    if plate:
        stmt = stmt.join(PlateRead, PlateRead.event_id == VehicleEvent.id).where(PlateRead.plate_text == plate)
    return list(db.execute(stmt).scalars().all())


def get_account(db: Session, plate_text: str) -> Account:
    account = db.execute(select(Account).where(Account.plate_text == plate_text)).scalar_one_or_none()
    if account is None:
        raise NotFoundError
    return account


def list_transactions(db: Session, account_id: str) -> list[Transaction]:
    return list(db.execute(select(Transaction).where(Transaction.account_id == account_id)).scalars().all())


def get_realtime_stats(db: Session) -> dict:
    total_in = db.execute(select(func.count()).where(VehicleEvent.direction == "in")).scalar_one()
    total_out = db.execute(select(func.count()).where(VehicleEvent.direction == "out")).scalar_one()
    total_events = db.execute(select(func.count()).select_from(VehicleEvent)).scalar_one()
    ocr_total = db.execute(select(func.count()).select_from(PlateRead).where(PlateRead.plate_text.is_not(None))).scalar_one()
    success_rate = (ocr_total / total_events * 100) if total_events else 0.0
    return {"total_in": total_in, "total_out": total_out, "ocr_success_rate": success_rate}


def get_ocr_rate(db: Session) -> float:
    total_events = db.execute(select(func.count()).select_from(PlateRead)).scalar_one()
    success_total = db.execute(
        select(func.count()).select_from(PlateRead).where(PlateRead.plate_text.is_not(None))
    ).scalar_one()
    return (success_total / total_events * 100) if total_events else 0.0


def get_traffic_stats(db: Session, group_by: str) -> list[dict]:
    _ = group_by
    return []
