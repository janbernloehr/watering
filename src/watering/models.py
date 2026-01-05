"""Data models for the watering system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Self


@dataclass(frozen=True, slots=True)
class WateringRecord:
    """Record of a watering event."""

    id: int | None
    waterdate: datetime
    user: str
    quantity: int

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a WateringRecord from a dictionary."""
        return cls(
            id=data.get("id"),
            waterdate=data["waterdate"],
            user=data["user"],
            quantity=data["quantity"],
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "waterdate": self.waterdate.isoformat(),
            "user": self.user,
            "quantity": self.quantity,
        }


@dataclass(frozen=True, slots=True)
class FillingRecord:
    """Record of a water can filling event."""

    id: int | None
    filldate: datetime
    user: str
    quantity: int

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a FillingRecord from a dictionary."""
        return cls(
            id=data.get("id"),
            filldate=data["filldate"],
            user=data["user"],
            quantity=data["quantity"],
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "filldate": self.filldate.isoformat(),
            "user": self.user,
            "quantity": self.quantity,
        }


@dataclass(frozen=True, slots=True)
class WateringHistory:
    """Complete watering history since last fill."""

    last_filling: FillingRecord
    remaining: int
    history: list[WateringRecord]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "last_filling": self.last_filling.to_dict(),
            "remaining": self.remaining,
            "history": [record.to_dict() for record in self.history],
        }
