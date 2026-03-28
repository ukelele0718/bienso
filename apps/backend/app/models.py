from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    gate_type: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    stream_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (CheckConstraint("gate_type IN ('student','staff')", name="ck_cameras_gate_type"),)


class VehicleEvent(Base):
    __tablename__ = "vehicle_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    camera_id: Mapped[str] = mapped_column(String, ForeignKey("cameras.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    direction: Mapped[str] = mapped_column(String, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String, nullable=False)
    track_id: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("direction IN ('in','out')", name="ck_vehicle_events_direction"),
        CheckConstraint("vehicle_type IN ('motorbike','car')", name="ck_vehicle_events_vehicle_type"),
    )


class PlateRead(Base):
    __tablename__ = "plate_reads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    event_id: Mapped[str] = mapped_column(String, ForeignKey("vehicle_events.id", ondelete="CASCADE"), nullable=False)
    plate_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    snapshot_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    crop_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (CheckConstraint("ocr_status IN ('success','partial','failed')", name="ck_plate_reads_ocr_status"),)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    plate_text: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    balance_vnd: Mapped[int] = mapped_column(Integer, nullable=False)
    registration_status: Mapped[str] = mapped_column(String, nullable=False, default="temporary_registered")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "registration_status IN ('registered','temporary_registered','unknown')",
            name="ck_accounts_registration_status",
        ),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    account_id: Mapped[str] = mapped_column(String, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[str | None] = mapped_column(String, ForeignKey("vehicle_events.id"), nullable=True)
    amount_vnd: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after_vnd: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (CheckConstraint("type IN ('init','event_charge','manual_adjust')", name="ck_transactions_type"),)


class BarrierAction(Base):
    __tablename__ = "barrier_actions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    event_id: Mapped[str] = mapped_column(String, ForeignKey("vehicle_events.id", ondelete="CASCADE"), nullable=False)
    plate_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    registration_status: Mapped[str] = mapped_column(String, nullable=False)
    barrier_action: Mapped[str] = mapped_column(String, nullable=False)
    barrier_reason: Mapped[str] = mapped_column(Text, nullable=False)
    needs_verification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verified_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "registration_status IN ('registered','temporary_registered','unknown')",
            name="ck_barrier_actions_registration_status",
        ),
        CheckConstraint("barrier_action IN ('open','hold')", name="ck_barrier_actions_action"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
