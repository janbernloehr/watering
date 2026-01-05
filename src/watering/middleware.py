"""Falcon middleware components."""

from typing import TYPE_CHECKING

from watering.config import CorsConfig

if TYPE_CHECKING:
    import falcon


class CORSMiddleware:
    """CORS middleware for Falcon."""

    def __init__(self, config: CorsConfig) -> None:
        """Initialize CORS middleware."""
        self._config = config

    def process_request(self, req: "falcon.Request", resp: "falcon.Response") -> None:
        """Process incoming request for CORS."""
        origin = req.get_header("Origin")

        if origin and self._should_allow_origin(origin):
            resp.set_header("Access-Control-Allow-Origin", origin)
            resp.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            resp.set_header("Access-Control-Allow-Headers", "Content-Type")

    def _should_allow_origin(self, origin: str) -> bool:
        """Check if origin should be allowed."""
        if self._config.allow_all_origins:
            return True
        return origin in self._config.allowed_origins
