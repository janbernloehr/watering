"""FastAPI routes for the watering system API."""

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Path

from watering.config import Config, get_config
from watering.database import WateringDatabase
from watering.models import ErrorResponse, FillResponse, WateringHistory, WaterResponse

if TYPE_CHECKING:
    from watering.hardware import WateringController

router = APIRouter(prefix="/watering.api", tags=["watering"])


def get_controller() -> "WateringController":
    """Dependency to get the watering controller. Overridden in app.py."""
    msg = "Controller not initialized - this dependency should be overridden"
    raise RuntimeError(msg)


def get_database(config: Annotated[Config, Depends(get_config)]) -> WateringDatabase:
    """Dependency to get database instance."""
    return WateringDatabase(config.database)


@router.get(
    "/water/{volume}",
    response_model=WaterResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Water plants",
    description="Activate the watering pump for a specified volume.",
)
async def water_plants(
    volume: Annotated[int, Path(gt=0, description="Volume in milliliters")],
    config: Annotated[Config, Depends(get_config)],
    database: Annotated[WateringDatabase, Depends(get_database)],
    controller: Annotated["WateringController", Depends(get_controller)],
) -> WaterResponse:
    """Water plants with the specified volume."""
    duration = controller.water(volume)
    database.record_watering(volume, config.default_user)

    return WaterResponse(volume=volume, duration=round(duration, 2))


@router.get(
    "/fill/{volume}",
    response_model=FillResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Record refill",
    description="Record a water tank refill event.",
)
async def record_fill(
    volume: Annotated[int, Path(gt=0, description="Volume in milliliters")],
    config: Annotated[Config, Depends(get_config)],
    database: Annotated[WateringDatabase, Depends(get_database)],
) -> FillResponse:
    """Record a water tank refill."""
    database.record_filling(volume, config.default_user)

    return FillResponse(volume=volume)


@router.get(
    "/history",
    response_model=WateringHistory,
    summary="Get history",
    description="Get watering history since the last refill.",
)
async def get_history(
    database: Annotated[WateringDatabase, Depends(get_database)],
) -> WateringHistory:
    """Get watering history."""
    return database.get_history()
