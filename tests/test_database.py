"""Tests for database module."""

from watering.database import WateringDatabase
from watering.models import FillingRecord, WateringHistory, WateringRecord


class TestWateringDatabase:
    """Tests for WateringDatabase."""

    def test_record_watering(self, database: WateringDatabase):
        """Test recording a watering event."""
        record = database.record_watering(250, "TestUser")

        assert isinstance(record, WateringRecord)
        assert record.quantity == 250
        assert record.user == "TestUser"

    def test_record_filling(self, database: WateringDatabase):
        """Test recording a filling event."""
        record = database.record_filling(2000, "TestUser")

        assert isinstance(record, FillingRecord)
        assert record.quantity == 2000
        assert record.user == "TestUser"

    def test_get_history_empty(self, database: WateringDatabase):
        """Test getting history when no fillings exist."""
        history = database.get_history()

        assert isinstance(history, WateringHistory)
        assert history.last_filling is None
        assert history.remaining == 0
        assert history.history == []

    def test_get_history_with_data(self, database: WateringDatabase):
        """Test getting history with filling and waterings."""
        database.record_filling(2000, "TestUser")
        database.record_watering(250, "TestUser")
        database.record_watering(150, "TestUser")

        history = database.get_history()

        assert isinstance(history, WateringHistory)
        assert history.last_filling is not None
        assert history.last_filling.quantity == 2000
        assert history.remaining == 1600  # 2000 - 250 - 150
        assert len(history.history) == 2

    def test_get_history_only_recent_waterings(self, database: WateringDatabase):
        """Test that only waterings after last fill are included."""
        database.record_filling(1000, "TestUser")
        database.record_watering(200, "TestUser")

        database.record_filling(2000, "TestUser")
        database.record_watering(300, "TestUser")

        history = database.get_history()

        assert history.last_filling is not None
        assert history.last_filling.quantity == 2000
        assert history.remaining == 1700  # 2000 - 300
        assert len(history.history) == 1
