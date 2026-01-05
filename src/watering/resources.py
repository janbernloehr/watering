"""Falcon resources (API endpoints)."""

import json
from typing import TYPE_CHECKING

import falcon

from watering.config import Config
from watering.database import WateringDatabase
from watering.hardware import WateringController

if TYPE_CHECKING:
    from falcon import Request, Response


class WateringResource:
    """Resource for watering operations."""

    def __init__(
        self,
        controller: WateringController,
        database: WateringDatabase,
        config: Config,
    ) -> None:
        """Initialize watering resource."""
        self._controller = controller
        self._database = database
        self._config = config

    def on_get(self, _req: "Request", resp: "Response", volume: str) -> None:
        """Handle watering request."""
        try:
            volume_ml = int(volume)
        except ValueError:
            resp.status = falcon.HTTP_400
            resp.media = {"error": "Invalid volume. Must be an integer."}
            return

        if volume_ml <= 0:
            resp.status = falcon.HTTP_400
            resp.media = {"error": "Volume must be positive."}
            return

        duration = self._controller.water(volume_ml)
        self._database.record_watering(volume_ml, self._config.default_user)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(
            {
                "action": "water",
                "volume": volume_ml,
                "duration": round(duration, 2),
            }
        )


class FillingResource:
    """Resource for recording water can fills."""

    def __init__(self, database: WateringDatabase, config: Config) -> None:
        """Initialize filling resource."""
        self._database = database
        self._config = config

    def on_get(self, _req: "Request", resp: "Response", volume: str) -> None:
        """Handle filling record request."""
        try:
            volume_ml = int(volume)
        except ValueError:
            resp.status = falcon.HTTP_400
            resp.media = {"error": "Invalid volume. Must be an integer."}
            return

        if volume_ml <= 0:
            resp.status = falcon.HTTP_400
            resp.media = {"error": "Volume must be positive."}
            return

        self._database.record_filling(volume_ml, self._config.default_user)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(
            {
                "action": "record_filling",
                "volume": volume_ml,
            }
        )


class HistoryResource:
    """Resource for retrieving watering history."""

    def __init__(self, database: WateringDatabase) -> None:
        """Initialize history resource."""
        self._database = database

    def on_get(self, _req: "Request", resp: "Response") -> None:
        """Handle history request."""
        history = self._database.get_history()

        if history is None:
            resp.status = falcon.HTTP_200
            resp.text = json.dumps(
                {
                    "last_filling": None,
                    "remaining": 0,
                    "history": [],
                }
            )
            return

        resp.status = falcon.HTTP_200
        resp.text = json.dumps(history.to_dict())


def create_resources(
    controller: WateringController,
    database: WateringDatabase,
    config: Config,
) -> dict[str, WateringResource | FillingResource | HistoryResource]:
    """Create all API resources."""
    return {
        "watering": WateringResource(controller, database, config),
        "filling": FillingResource(database, config),
        "history": HistoryResource(database),
    }
