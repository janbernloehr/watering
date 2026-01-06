"""FastAPI application module."""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from watering.config import Config, get_config
from watering.hardware import WateringController, create_gpio
from watering.routes import get_controller, router

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Global controller instance (initialized at startup)
_controller: WateringController | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> "AsyncGenerator[None]":
    """Application lifespan handler for startup/shutdown."""
    global _controller  # noqa: PLW0603

    config = get_config()
    use_mock = getattr(app.state, "use_mock_gpio", True)

    gpio = create_gpio(use_mock=use_mock)
    _controller = WateringController(config.hardware, gpio)
    _controller.initialize()

    yield

    _controller = None


def create_app(
    config: Config | None = None,
    *,
    use_mock_gpio: bool = False,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        config: Application configuration. If None, uses default config.
        use_mock_gpio: If True, use mock GPIO for testing.

    Returns:
        Configured FastAPI application.
    """
    if config is None:
        config = get_config()

    app = FastAPI(
        title="Watering API",
        description="Smart plant watering system REST API",
        version="0.3.0",
        lifespan=lifespan,
    )

    # Store config for lifespan
    app.state.use_mock_gpio = use_mock_gpio

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,  # ty: ignore[invalid-argument-type]
        allow_origins=["*"] if config.cors.allow_all_origins else list(config.cors.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Override controller dependency to provide our initialized controller
    def _get_controller() -> WateringController:
        if _controller is None:
            msg = "Controller not initialized"
            raise RuntimeError(msg)
        return _controller

    app.dependency_overrides[get_controller] = _get_controller

    # Include routes
    app.include_router(router)

    return app


# ASGI application instance for uvicorn
app = create_app(use_mock_gpio=True)


def main() -> None:
    """Run development server."""
    import uvicorn  # noqa: PLC0415

    uvicorn.run(
        "watering.app:app",
        host="0.0.0.0",  # noqa: S104
        port=8087,
        reload=True,
    )


if __name__ == "__main__":
    main()
