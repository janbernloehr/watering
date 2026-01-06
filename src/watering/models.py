"""Pydantic models for the watering system API."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field


class WateringRecord(BaseModel):
    """Record of a watering event."""

    id: int | None = None
    waterdate: datetime
    user: str
    quantity: int = Field(gt=0, description="Volume in milliliters")

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a WateringRecord from a database row."""
        return cls(
            id=data.get("id"),
            waterdate=data["waterdate"],
            user=data["user"],
            quantity=data["quantity"],
        )


class FillingRecord(BaseModel):
    """Record of a water can filling event."""

    id: int | None = None
    filldate: datetime
    user: str
    quantity: int = Field(gt=0, description="Volume in milliliters")

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a FillingRecord from a database row."""
        return cls(
            id=data.get("id"),
            filldate=data["filldate"],
            user=data["user"],
            quantity=data["quantity"],
        )


class WateringHistory(BaseModel):
    """Complete watering history since last fill."""

    last_filling: FillingRecord | None = None
    remaining: int = 0
    history: list[WateringRecord] = Field(default_factory=list)


# API Response Models
class WaterResponse(BaseModel):
    """Response for watering action."""

    action: str = "water"
    volume: int
    duration: float


class FillResponse(BaseModel):
    """Response for fill action."""

    action: str = "record_filling"
    volume: int


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
