from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Must be set before importing app modules using settings
os.environ.setdefault(
    "APP_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr_test",
)

from app.db import get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def db_engine():
    url = os.environ["APP_DATABASE_URL"]
    engine = create_engine(url, pool_pre_ping=True)

    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    with engine.begin() as conn:
        for migration in migration_files:
            sql = migration.read_text(encoding="utf-8")
            if sql.strip():
                conn.execute(text(sql))

    yield engine

    engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = TestingSessionLocal()

    # Seed camera required by FK vehicle_events.camera_id -> cameras.id
    with db_engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO cameras (id, name, gate_type, location, stream_url, is_active)
                VALUES (:id, :name, :gate_type, :location, :stream_url, :is_active)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "Test Camera",
                "gate_type": "student",
                "location": "Test Gate",
                "stream_url": "rtsp://test/stream",
                "is_active": True,
            },
        )

    try:
        yield db
    finally:
        db.close()

    with db_engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE barrier_actions, transactions, plate_reads, vehicle_events, accounts, cameras, audit_logs RESTART IDENTITY CASCADE;"
            )
        )


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
