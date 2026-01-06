"""Tests for Pydantic models."""

from datetime import UTC, datetime

from watering.models import FillingRecord, WateringHistory, WateringRecord


class TestWateringRecord:
    """Tests for WateringRecord."""

    def test_from_dict(self):
        """Test creating record from dictionary."""
        now = datetime.now(UTC)
        data = {
            "id": 1,
            "waterdate": now,
            "user": "TestUser",
            "quantity": 250,
        }
        record = WateringRecord.from_dict(data)

        assert record.id == 1
        assert record.waterdate == now
        assert record.user == "TestUser"
        assert record.quantity == 250

    def test_model_dump(self):
        """Test Pydantic model serialization."""
        now = datetime.now(UTC)
        record = WateringRecord(
            id=1,
            waterdate=now,
            user="TestUser",
            quantity=250,
        )
        data = record.model_dump()

        assert data["waterdate"] == now
        assert data["user"] == "TestUser"
        assert data["quantity"] == 250
        assert data["id"] == 1

    def test_json_serialization(self):
        """Test JSON serialization."""
        now = datetime.now(UTC)
        record = WateringRecord(
            waterdate=now,
            user="TestUser",
            quantity=250,
        )
        json_str = record.model_dump_json()

        assert "TestUser" in json_str
        assert "250" in json_str


class TestFillingRecord:
    """Tests for FillingRecord."""

    def test_from_dict(self):
        """Test creating record from dictionary."""
        now = datetime.now(UTC)
        data = {
            "id": 1,
            "filldate": now,
            "user": "TestUser",
            "quantity": 2000,
        }
        record = FillingRecord.from_dict(data)

        assert record.id == 1
        assert record.filldate == now
        assert record.user == "TestUser"
        assert record.quantity == 2000

    def test_model_dump(self):
        """Test Pydantic model serialization."""
        now = datetime.now(UTC)
        record = FillingRecord(
            id=1,
            filldate=now,
            user="TestUser",
            quantity=2000,
        )
        data = record.model_dump()

        assert data["filldate"] == now
        assert data["user"] == "TestUser"
        assert data["quantity"] == 2000


class TestWateringHistory:
    """Tests for WateringHistory."""

    def test_model_dump(self):
        """Test Pydantic model serialization."""
        now = datetime.now(UTC)
        filling = FillingRecord(id=1, filldate=now, user="User", quantity=2000)
        watering = WateringRecord(id=1, waterdate=now, user="User", quantity=250)

        history = WateringHistory(
            last_filling=filling,
            remaining=1750,
            history=[watering],
        )
        data = history.model_dump()

        assert data["remaining"] == 1750
        assert data["last_filling"] is not None
        assert len(data["history"]) == 1

    def test_empty_history(self):
        """Test empty history defaults."""
        history = WateringHistory()

        assert history.last_filling is None
        assert history.remaining == 0
        assert history.history == []
