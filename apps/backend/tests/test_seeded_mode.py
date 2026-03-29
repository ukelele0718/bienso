"""
Test Seeded Mode Backend Functionality

Tests for:
1. decide_barrier service function - all registration status + direction combinations
2. Account import scenarios - registration, balance, transactions
3. API endpoints - accounts listing, filtering, summary
"""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Account, Transaction
from app.services import decide_barrier

TEST_CAMERA_ID = "11111111-1111-1111-1111-111111111111"


# =============================================================================
# Part 1: Test decide_barrier function (services.py)
# =============================================================================


class TestDecideBarrier:
    """Test all barrier decision rules for seeded mode."""

    def test_registered_in_opens_barrier(self) -> None:
        """registered + in -> barrier opens immediately."""
        decision = decide_barrier("registered", "in")

        assert decision.barrier_action == "open"
        assert decision.registration_status == "registered"
        assert decision.barrier_reason == "registered_vehicle_in"
        assert decision.needs_verification is False

    def test_registered_out_opens_barrier(self) -> None:
        """registered + out -> barrier opens (NEW RULE for seeded mode)."""
        decision = decide_barrier("registered", "out")

        assert decision.barrier_action == "open"
        assert decision.registration_status == "registered"
        assert decision.barrier_reason == "registered_vehicle_out"
        assert decision.needs_verification is False

    def test_temporary_registered_in_opens_barrier(self) -> None:
        """temporary_registered + in -> barrier opens."""
        decision = decide_barrier("temporary_registered", "in")

        assert decision.barrier_action == "open"
        assert decision.registration_status == "temporary_registered"
        assert decision.barrier_reason == "unknown_vehicle_auto_temporary_register"
        assert decision.needs_verification is False

    def test_temporary_registered_out_holds_barrier(self) -> None:
        """temporary_registered + out -> barrier holds for verification."""
        decision = decide_barrier("temporary_registered", "out")

        assert decision.barrier_action == "hold"
        assert decision.registration_status == "temporary_registered"
        assert decision.barrier_reason == "temporary_vehicle_out_requires_verify"
        assert decision.needs_verification is True

    def test_unknown_in_auto_registers_and_opens(self) -> None:
        """unknown + in -> changes to temporary_registered, barrier opens."""
        decision = decide_barrier("unknown", "in")

        assert decision.barrier_action == "open"
        assert decision.registration_status == "temporary_registered"  # Status changes!
        assert decision.barrier_reason == "unknown_vehicle_auto_temporary_register"
        assert decision.needs_verification is False

    def test_unknown_out_holds_barrier(self) -> None:
        """unknown + out -> default hold behavior."""
        decision = decide_barrier("unknown", "out")

        assert decision.barrier_action == "hold"
        assert decision.registration_status == "unknown"
        assert decision.barrier_reason == "default_hold"
        assert decision.needs_verification is True

    def test_default_case_holds_barrier(self) -> None:
        """Any unhandled combination -> default hold."""
        decision = decide_barrier("invalid_status", "in")

        assert decision.barrier_action == "hold"
        assert decision.barrier_reason == "default_hold"
        assert decision.needs_verification is True


# =============================================================================
# Part 2: Test Import Scenarios (Account Creation via Events)
# =============================================================================


def _event_payload(
    plate_text: str,
    direction: str = "in",
    vehicle_type: str = "motorbike",
    track_id: str | None = None,
) -> dict:
    """Create a standard event payload for testing."""
    return {
        "camera_id": TEST_CAMERA_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "direction": direction,
        "vehicle_type": vehicle_type,
        "track_id": track_id or f"track-{uuid4().hex[:8]}",
        "plate_text": plate_text,
        "confidence": 0.95,
        "snapshot_url": None,
    }


class TestAccountImportScenarios:
    """Test account creation behavior when new plates are detected."""

    def test_new_plate_creates_temporary_registered_account(
        self, client: TestClient, db_session: Session
    ) -> None:
        """First-time plate detection creates account with temporary_registered status."""
        plate = "29A-11111"

        res = client.post("/api/v1/events", json=_event_payload(plate))
        assert res.status_code == 200

        # Verify account was created
        account = db_session.query(Account).filter(Account.plate_text == plate).first()
        assert account is not None
        assert account.registration_status == "temporary_registered"

    def test_new_plate_gets_initial_balance(
        self, client: TestClient, db_session: Session
    ) -> None:
        """New accounts receive initial balance of 100,000 VND (minus first charge)."""
        plate = "29A-22222"

        client.post("/api/v1/events", json=_event_payload(plate))

        account = db_session.query(Account).filter(Account.plate_text == plate).first()
        assert account is not None
        # Initial balance is 100000, minus 2000 charge = 98000
        assert account.balance_vnd == 98_000

    def test_new_plate_creates_init_transaction(
        self, client: TestClient, db_session: Session
    ) -> None:
        """New accounts get an 'init' transaction for the initial balance."""
        plate = "29A-33333"

        client.post("/api/v1/events", json=_event_payload(plate))

        account = db_session.query(Account).filter(Account.plate_text == plate).first()
        assert account is not None

        init_tx = (
            db_session.query(Transaction)
            .filter(Transaction.account_id == account.id, Transaction.type == "init")
            .first()
        )
        assert init_tx is not None
        assert init_tx.amount_vnd == 100_000
        assert init_tx.balance_after_vnd == 100_000

    def test_duplicate_plate_does_not_create_duplicate_account(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Multiple events for same plate should not create duplicate accounts."""
        plate = "29A-44444"

        # Send multiple events for same plate
        client.post("/api/v1/events", json=_event_payload(plate, track_id="track-1"))
        client.post("/api/v1/events", json=_event_payload(plate, track_id="track-2"))
        client.post("/api/v1/events", json=_event_payload(plate, track_id="track-3"))

        # Should only have one account
        accounts = db_session.query(Account).filter(Account.plate_text == plate).all()
        assert len(accounts) == 1

    def test_duplicate_plate_only_one_init_transaction(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Multiple events for same plate should only create one init transaction."""
        plate = "29A-55555"

        client.post("/api/v1/events", json=_event_payload(plate, track_id="track-1"))
        client.post("/api/v1/events", json=_event_payload(plate, track_id="track-2"))

        account = db_session.query(Account).filter(Account.plate_text == plate).first()
        init_txs = (
            db_session.query(Transaction)
            .filter(Transaction.account_id == account.id, Transaction.type == "init")
            .all()
        )
        assert len(init_txs) == 1


class TestPreRegisteredAccountBehavior:
    """Test behavior for pre-registered accounts (seeded mode)."""

    def test_registered_account_gets_open_on_entry(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Pre-registered accounts get barrier open on entry."""
        plate = "30A-REG01"

        # Create a pre-registered account
        account = Account(
            id=str(uuid4()),
            plate_text=plate,
            balance_vnd=100_000,
            registration_status="registered",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(account)
        db_session.commit()

        res = client.post("/api/v1/events", json=_event_payload(plate, "in"))
        assert res.status_code == 200

        body = res.json()
        assert body["registration_status"] == "registered"
        assert body["barrier_action"] == "open"
        assert body["needs_verification"] is False

    def test_registered_account_gets_open_on_exit(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Pre-registered accounts get barrier open on exit (seeded mode rule)."""
        plate = "30A-REG02"

        # Create a pre-registered account
        account = Account(
            id=str(uuid4()),
            plate_text=plate,
            balance_vnd=100_000,
            registration_status="registered",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(account)
        db_session.commit()

        res = client.post("/api/v1/events", json=_event_payload(plate, "out"))
        assert res.status_code == 200

        body = res.json()
        assert body["registration_status"] == "registered"
        assert body["barrier_action"] == "open"
        assert body["barrier_reason"] == "registered_vehicle_out"


# =============================================================================
# Part 3: Test API Endpoints
# =============================================================================


class TestAccountsListAPI:
    """Test GET /api/v1/accounts endpoint."""

    def test_list_accounts_returns_paginated_results(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Accounts list returns paginated response structure."""
        # Create some accounts
        for i in range(5):
            db_session.add(
                Account(
                    id=str(uuid4()),
                    plate_text=f"29A-PAGE{i}",
                    balance_vnd=100_000,
                    registration_status="registered",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
        db_session.commit()

        res = client.get("/api/v1/accounts?page=1&page_size=3")
        assert res.status_code == 200

        body = res.json()
        assert "items" in body
        assert "total" in body
        assert "page" in body
        assert "page_size" in body
        assert body["page"] == 1
        assert body["page_size"] == 3
        assert len(body["items"]) <= 3

    def test_list_accounts_filter_by_plate(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Accounts list filters by plate text (partial match)."""
        # Create accounts with different plate prefixes
        db_session.add(
            Account(
                id=str(uuid4()),
                plate_text="29A-FILTER1",
                balance_vnd=100_000,
                registration_status="registered",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        db_session.add(
            Account(
                id=str(uuid4()),
                plate_text="29A-FILTER2",
                balance_vnd=100_000,
                registration_status="registered",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        db_session.add(
            Account(
                id=str(uuid4()),
                plate_text="30B-OTHER",
                balance_vnd=100_000,
                registration_status="registered",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        db_session.commit()

        res = client.get("/api/v1/accounts?plate=29A-FILTER")
        assert res.status_code == 200

        body = res.json()
        assert all("29A-FILTER" in item["plate_text"] for item in body["items"])

    def test_list_accounts_filter_by_registration_status(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Accounts list filters by registration_status."""
        # Create accounts with different statuses
        db_session.add(
            Account(
                id=str(uuid4()),
                plate_text="29A-STAT1",
                balance_vnd=100_000,
                registration_status="registered",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        db_session.add(
            Account(
                id=str(uuid4()),
                plate_text="29A-STAT2",
                balance_vnd=100_000,
                registration_status="temporary_registered",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        db_session.commit()

        res = client.get("/api/v1/accounts?registration_status=registered")
        assert res.status_code == 200

        body = res.json()
        assert all(
            item["registration_status"] == "registered" for item in body["items"]
        )


class TestAccountsSummaryAPI:
    """Test GET /api/v1/accounts/summary endpoint."""

    def test_summary_returns_correct_counts(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Summary endpoint returns correct account counts by status."""
        # Create accounts with different statuses
        for i in range(3):
            db_session.add(
                Account(
                    id=str(uuid4()),
                    plate_text=f"29A-SUM-REG{i}",
                    balance_vnd=100_000,
                    registration_status="registered",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
        for i in range(2):
            db_session.add(
                Account(
                    id=str(uuid4()),
                    plate_text=f"29A-SUM-TEMP{i}",
                    balance_vnd=100_000,
                    registration_status="temporary_registered",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
        db_session.commit()

        res = client.get("/api/v1/accounts/summary")
        assert res.status_code == 200

        body = res.json()
        assert "total_accounts" in body
        assert "registered_accounts" in body
        assert "temporary_registered_accounts" in body

        # Verify counts are at least what we added
        # (may be more from other tests due to session scope)
        assert body["registered_accounts"] >= 3
        assert body["temporary_registered_accounts"] >= 2
        assert body["total_accounts"] >= 5

    def test_summary_structure_matches_schema(self, client: TestClient) -> None:
        """Summary response has expected structure."""
        res = client.get("/api/v1/accounts/summary")
        assert res.status_code == 200

        body = res.json()
        assert isinstance(body["total_accounts"], int)
        assert isinstance(body["registered_accounts"], int)
        assert isinstance(body["temporary_registered_accounts"], int)


class TestGetSingleAccountAPI:
    """Test GET /api/v1/accounts/{plate_text} endpoint."""

    def test_get_account_returns_details(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Get single account returns full details."""
        plate = "29A-SINGLE"
        db_session.add(
            Account(
                id=str(uuid4()),
                plate_text=plate,
                balance_vnd=75_000,
                registration_status="registered",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        db_session.commit()

        res = client.get(f"/api/v1/accounts/{plate}")
        assert res.status_code == 200

        body = res.json()
        assert body["plate_text"] == plate
        assert body["balance_vnd"] == 75_000
        assert body["registration_status"] == "registered"

    def test_get_account_not_found_returns_404(self, client: TestClient) -> None:
        """Get non-existent account returns 404."""
        res = client.get("/api/v1/accounts/NONEXISTENT-123")
        assert res.status_code == 404


class TestAccountTransactionsAPI:
    """Test GET /api/v1/accounts/{plate_text}/transactions endpoint."""

    def test_list_transactions_returns_history(
        self, client: TestClient, db_session: Session
    ) -> None:
        """List transactions returns account transaction history."""
        plate = "29A-TXHIST"

        # Create account with transactions
        account = Account(
            id=str(uuid4()),
            plate_text=plate,
            balance_vnd=95_000,
            registration_status="registered",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(account)
        db_session.flush()

        db_session.add(
            Transaction(
                id=str(uuid4()),
                account_id=account.id,
                event_id=None,
                amount_vnd=100_000,
                balance_after_vnd=100_000,
                type="init",
                created_at=datetime.utcnow(),
            )
        )
        db_session.commit()

        res = client.get(f"/api/v1/accounts/{plate}/transactions")
        assert res.status_code == 200

        body = res.json()
        assert isinstance(body, list)
        assert len(body) >= 1

        # Check transaction structure
        tx = body[0]
        assert "id" in tx
        assert "account_id" in tx
        assert "amount_vnd" in tx
        assert "balance_after_vnd" in tx
        assert "type" in tx
        assert "created_at" in tx
