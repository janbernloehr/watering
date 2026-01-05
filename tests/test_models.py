"""Tests for data models."""

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

    def test_to_dict(self):
        """Test converting record to dictionary."""
        now = datetime.now(UTC)
        record = WateringRecord(
            id=1,
            waterdate=now,
            user="TestUser",
            quantity=250,
        )
        data = record.to_dict()

        assert data["waterdate"] == now.isoformat()
        assert data["user"] == "TestUser"
        assert data["quantity"] == 250
        assert "id" not in data


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

    def test_to_dict(self):
        """Test converting record to dictionary."""
        now = datetime.now(UTC)
        record = FillingRecord(
            id=1,
            filldate=now,
            user="TestUser",
            quantity=2000,
        )
        data = record.to_dict()

        assert data["filldate"] == now.isoformat()
        assert data["user"] == "TestUser"
        assert data["quantity"] == 2000


class TestWateringHistory:
    """Tests for WateringHistory."""

    def test_to_dict(self):
        """Test converting history to dictionary."""
        now = datetime.now(UTC)
        filling = FillingRecord(id=1, filldate=now, user="User", quantity=2000)
        watering = WateringRecord(id=1, waterdate=now, user="User", quantity=250)

        history = WateringHistory(
            last_filling=filling,
            remaining=1750,
            history=[watering],
        )
        data = history.to_dict()

        assert data["remaining"] == 1750
        assert "last_filling" in data
        assert len(data["history"]) == 1
