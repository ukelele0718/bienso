from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Use isolated SQLite DB for tests by default
os.environ.setdefault("APP_DATABASE_URL", "sqlite+pysqlite:///./test_backend.db")

from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    Account,
    AuditLog,
    BarrierAction,
    Camera,
    PlateRead,
    PretrainedDetection,
    PretrainedJob,
    Transaction,
    VehicleEvent,
)


@pytest.fixture(scope="session")
def db_engine():
    url = os.environ["APP_DATABASE_URL"]
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = TestingSessionLocal()

    # Seed camera required by FK vehicle_events.camera_id -> cameras.id
    db.add(
        Camera(
            id="11111111-1111-1111-1111-111111111111",
            name="Test Camera",
            gate_type="student",
            location="Test Gate",
            stream_url="rtsp://test/stream",
            is_active=True,
        )
    )
    db.commit()

    try:
        yield db
    finally:
        db.close()

    cleanup = TestingSessionLocal()
    try:
        for model in (
            PretrainedDetection,
            PretrainedJob,
            BarrierAction,
            Transaction,
            PlateRead,
            VehicleEvent,
            Account,
            Camera,
            AuditLog,
        ):
            cleanup.query(model).delete()
        cleanup.commit()
    finally:
        cleanup.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
