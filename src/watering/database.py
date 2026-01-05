"""Database operations for the watering system."""

from contextlib import contextmanager
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import dataset

from watering.config import DatabaseConfig
from watering.models import FillingRecord, WateringHistory, WateringRecord

if TYPE_CHECKING:
    from collections.abc import Generator


class WateringDatabase:
    """Database interface for watering operations."""

    def __init__(self, config: DatabaseConfig) -> None:
        """Initialize database connection."""
        self._config = config

    @contextmanager
    def _connection(self) -> "Generator[dataset.Database]":
        """Get a database connection context."""
        db = dataset.connect(self._config.connection_string)
        try:
            yield db
        finally:
            db.close()

    def record_watering(self, quantity: int, user: str) -> WateringRecord:
        """Record a watering event."""
        now = datetime.now(UTC)
        with self._connection() as db:
            waterings = db["waterings"]
            waterings.insert({"waterdate": now, "user": user, "quantity": quantity})
        return WateringRecord(id=None, waterdate=now, user=user, quantity=quantity)

    def record_filling(self, quantity: int, user: str) -> FillingRecord:
        """Record a water can filling event."""
        now = datetime.now(UTC)
        with self._connection() as db:
            fillings = db["fillings"]
            fillings.insert({"filldate": now, "user": user, "quantity": quantity})
        return FillingRecord(id=None, filldate=now, user=user, quantity=quantity)

    def get_history(self) -> WateringHistory | None:
        """Get watering history since the last fill."""
        with self._connection() as db:
            fillings = db["fillings"]
            last_filling_data = fillings.find_one(order_by="-filldate", _limit=1)

            if last_filling_data is None:
                return None

            last_filling = FillingRecord.from_dict(last_filling_data)
            waterings = db["waterings"]
            recent_waterings = waterings.find(
                waterings.table.columns.waterdate >= last_filling.filldate,
                order_by="-waterdate",
            )

            history: list[WateringRecord] = []
            total_taken = 0

            for watering_data in recent_waterings:
                record = WateringRecord.from_dict(watering_data)
                history.append(record)
                total_taken += record.quantity

            remaining = last_filling.quantity - total_taken

        return WateringHistory(
            last_filling=last_filling,
            remaining=remaining,
            history=history,
        )
