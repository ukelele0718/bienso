from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4
import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .models import Account, AuditLog, BarrierAction, Camera, ImportBatch, PlateRead, Transaction, VehicleEvent
from .services import decide_barrier


class NotFoundError(Exception):
    pass


def normalize_plate_text(plate_text: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]", "", plate_text or "").upper()
    return normalized


def create_event(db: Session, payload: dict) -> tuple[VehicleEvent, BarrierAction | None]:
    camera_id = payload["camera_id"]
    camera = db.execute(select(Camera).where(Camera.id == camera_id)).scalar_one_or_none()
    if camera is None:
        camera = Camera(
            id=camera_id,
            name=f"Auto camera {camera_id[:8]}",
            gate_type="student",
            location="auto_seeded_mode",
            stream_url=None,
            is_active=True,
            created_at=datetime.now(UTC),
        )
        db.add(camera)
        db.flush()

    event = VehicleEvent(
        id=str(uuid4()),
        camera_id=camera_id,
        timestamp=payload["timestamp"],
        direction=payload["direction"],
        vehicle_type=payload["vehicle_type"],
        track_id=payload["track_id"],
    )
    db.add(event)
    db.flush()

    raw_plate_text = payload.get("plate_text")
    plate_text = normalize_plate_text(raw_plate_text) if raw_plate_text else None
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

    barrier_action_row: BarrierAction | None = None

    if plate_text:
        account = db.execute(select(Account).where(Account.plate_text == plate_text)).scalar_one_or_none()

        if account is None:
            account = Account(
                id=str(uuid4()),
                plate_text=plate_text,
                balance_vnd=settings.initial_balance_vnd,
                registration_status="temporary_registered",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
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

        decision = decide_barrier(account.registration_status, payload["direction"])
        if account.registration_status != decision.registration_status:
            account.registration_status = decision.registration_status

        barrier_action_row = BarrierAction(
            id=str(uuid4()),
            event_id=event.id,
            plate_text=plate_text,
            registration_status=decision.registration_status,
            barrier_action=decision.barrier_action,
            barrier_reason=decision.barrier_reason,
            needs_verification=decision.needs_verification,
            verified_by=None,
            verified_at=None,
            created_at=payload["timestamp"],
        )
        db.add(barrier_action_row)

        db.add(
            AuditLog(
                id=str(uuid4()),
                user_id=None,
                action="barrier_decision",
                metadata_json={
                    "event_id": event.id,
                    "plate_text": plate_text,
                    "barrier_action": decision.barrier_action,
                    "barrier_reason": decision.barrier_reason,
                    "needs_verification": decision.needs_verification,
                },
                created_at=payload["timestamp"],
            )
        )

        account.balance_vnd -= settings.charge_per_event_vnd
        account.updated_at = datetime.now(UTC)
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
    if barrier_action_row:
        db.refresh(barrier_action_row)
    return event, barrier_action_row


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
        normalized_plate = normalize_plate_text(plate)
        stmt = stmt.join(PlateRead, PlateRead.event_id == VehicleEvent.id).where(PlateRead.plate_text == normalized_plate)
    return list(db.execute(stmt.order_by(VehicleEvent.timestamp.desc())).scalars().all())


def get_event_plate_meta(db: Session, event_id: str) -> PlateRead | None:
    return db.execute(select(PlateRead).where(PlateRead.event_id == event_id)).scalar_one_or_none()


def get_event_barrier_meta(db: Session, event_id: str) -> BarrierAction | None:
    return db.execute(select(BarrierAction).where(BarrierAction.event_id == event_id)).scalar_one_or_none()


def get_account(db: Session, plate_text: str) -> Account:
    normalized_plate = normalize_plate_text(plate_text)
    account = db.execute(select(Account).where(Account.plate_text == normalized_plate)).scalar_one_or_none()
    if account is None:
        raise NotFoundError
    return account


def list_transactions(db: Session, account_id: str) -> list[Transaction]:
    return list(
        db.execute(select(Transaction).where(Transaction.account_id == account_id).order_by(Transaction.created_at.asc()))
        .scalars()
        .all()
    )


def list_barrier_actions(db: Session, plate_text: str | None = None) -> list[BarrierAction]:
    stmt = select(BarrierAction)
    if plate_text:
        normalized_plate = normalize_plate_text(plate_text)
        stmt = stmt.where(BarrierAction.plate_text == normalized_plate)
    return list(db.execute(stmt.order_by(BarrierAction.created_at.asc())).scalars().all())


def verify_latest_hold(db: Session, plate_text: str, actor: str) -> BarrierAction:
    normalized_plate = normalize_plate_text(plate_text)
    row = db.execute(
        select(BarrierAction)
        .where(BarrierAction.plate_text == normalized_plate)
        .order_by(BarrierAction.created_at.desc())
    ).scalars().first()
    if row is None:
        raise NotFoundError
    if row.barrier_action != "hold":
        return row
    row.barrier_action = "open"
    row.barrier_reason = "manual_verify_open"
    row.needs_verification = False
    row.verified_by = actor
    row.verified_at = datetime.now(UTC)

    db.add(
        AuditLog(
            id=str(uuid4()),
            user_id=actor,
            action="barrier_verify",
            metadata_json={
                "plate_text": plate_text,
                "event_id": row.event_id,
                "result": "open",
            },
            created_at=datetime.now(UTC),
        )
    )

    db.commit()
    db.refresh(row)
    return row


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
    if group_by not in {"hour", "day"}:
        group_by = "hour"
    if group_by == "hour":
        bucket_expr = func.to_char(VehicleEvent.timestamp, "YYYY-MM-DD HH24:00")
    else:
        bucket_expr = func.to_char(VehicleEvent.timestamp, "YYYY-MM-DD")

    rows = db.execute(
        select(
            bucket_expr.label("bucket"),
            func.count().filter(VehicleEvent.direction == "in").label("total_in"),
            func.count().filter(VehicleEvent.direction == "out").label("total_out"),
        )
        .group_by(bucket_expr)
        .order_by(bucket_expr)
    ).all()

    return [{"bucket": r.bucket, "total_in": int(r.total_in or 0), "total_out": int(r.total_out or 0)} for r in rows]


def list_accounts(
    db: Session,
    plate: str | None,
    registration_status: str | None,
    page: int,
    page_size: int,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[Account], int]:
    stmt = select(Account)
    if plate:
        normalized_plate = normalize_plate_text(plate)
        stmt = stmt.where(Account.plate_text.ilike(f"%{normalized_plate}%"))
    if registration_status:
        stmt = stmt.where(Account.registration_status == registration_status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size

    sort_mapping = {
        "created_at": Account.created_at,
        "balance_vnd": Account.balance_vnd,
        "plate_text": Account.plate_text,
    }
    sort_column = sort_mapping.get(sort_by, Account.created_at)
    if sort_order == "asc":
        stmt = stmt.order_by(sort_column.asc())
    else:
        stmt = stmt.order_by(sort_column.desc())

    stmt = stmt.offset(offset).limit(page_size)
    accounts = list(db.execute(stmt).scalars().all())

    return accounts, total


def get_accounts_summary(db: Session) -> dict:
    total = db.execute(select(func.count()).select_from(Account)).scalar_one()
    registered = db.execute(
        select(func.count()).select_from(Account).where(Account.registration_status == "registered")
    ).scalar_one()
    temporary_registered = db.execute(
        select(func.count()).select_from(Account).where(Account.registration_status == "temporary_registered")
    ).scalar_one()

    return {
        "total_accounts": total,
        "registered_accounts": registered,
        "temporary_registered_accounts": temporary_registered,
    }


def list_import_batches(db: Session, limit: int = 20) -> list[ImportBatch]:
    stmt = select(ImportBatch).order_by(ImportBatch.created_at.desc()).limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_import_batches_summary(db: Session) -> dict:
    total_batches = db.execute(select(func.count()).select_from(ImportBatch)).scalar_one()
    sums = db.execute(
        select(
            func.coalesce(func.sum(ImportBatch.imported_count), 0),
            func.coalesce(func.sum(ImportBatch.skipped_count), 0),
            func.coalesce(func.sum(ImportBatch.invalid_count), 0),
        )
    ).one()

    return {
        "total_batches": int(total_batches or 0),
        "total_imported": int(sums[0] or 0),
        "total_skipped": int(sums[1] or 0),
        "total_invalid": int(sums[2] or 0),
    }


def mark_account_registered(db: Session, plate_text: str) -> Account:
    account = get_account(db, plate_text)
    if account.registration_status != "registered":
        account.registration_status = "registered"
        account.updated_at = datetime.utcnow()
        db.add(account)
        db.add(
            AuditLog(
                id=str(uuid4()),
                user_id=None,
                action="account_mark_registered",
                metadata_json={"plate_text": plate_text},
                created_at=datetime.utcnow(),
            )
        )
        db.commit()
        db.refresh(account)
    return account


def adjust_account_balance(
    db: Session,
    plate_text: str,
    amount_vnd: int,
    actor: str | None = None,
    reason: str | None = None,
) -> tuple[Account, Transaction]:
    account = get_account(db, plate_text)
    account.balance_vnd += amount_vnd
    account.updated_at = datetime.utcnow()

    tx = Transaction(
        id=str(uuid4()),
        account_id=account.id,
        event_id=None,
        amount_vnd=amount_vnd,
        balance_after_vnd=account.balance_vnd,
        type="manual_adjust",
        created_at=datetime.utcnow(),
    )

    db.add(account)
    db.add(tx)
    db.add(
        AuditLog(
            id=str(uuid4()),
            user_id=actor,
            action="account_adjust_balance",
            metadata_json={
                "plate_text": plate_text,
                "amount_vnd": amount_vnd,
                "reason": reason,
            },
            created_at=datetime.utcnow(),
        )
    )
    db.commit()
    db.refresh(account)
    db.refresh(tx)
    return account, tx
