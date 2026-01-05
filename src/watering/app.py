"""Main application module."""

import falcon

from watering.config import Config, get_config
from watering.database import WateringDatabase
from watering.hardware import WateringController, create_gpio
from watering.middleware import CORSMiddleware
from watering.resources import create_resources


def create_app(config: Config | None = None, *, use_mock_gpio: bool = False) -> falcon.App:
    """
    Create and configure the Falcon application.

    Args:
        config: Application configuration. If None, uses default config.
        use_mock_gpio: If True, use mock GPIO for testing.

    Returns:
        Configured Falcon application.
    """
    if config is None:
        config = get_config()

    # Initialize components
    gpio = create_gpio(use_mock=use_mock_gpio)
    controller = WateringController(config.hardware, gpio)
    database = WateringDatabase(config.database)

    # Initialize hardware
    controller.initialize()

    # Create middleware
    cors = CORSMiddleware(config.cors)

    # Create application
    app = falcon.App(middleware=[cors])

    # Create and register resources
    resources = create_resources(controller, database, config)

    app.add_route("/watering.api/water/{volume}", resources["watering"])
    app.add_route("/watering.api/fill/{volume}", resources["filling"])
    app.add_route("/watering.api/history", resources["history"])

    return app


# WSGI application instance for gunicorn
app = create_app(use_mock_gpio=True)


def main() -> None:
    """Run development server."""
    from wsgiref.simple_server import make_server  # noqa: PLC0415

    config = get_config()
    application = create_app(config, use_mock_gpio=True)

    print("Starting development server on http://localhost:8087")  # noqa: T201
    with make_server("", 8087, application) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
