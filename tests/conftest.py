"""Pytest configuration and fixtures."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from watering.config import Config, CorsConfig, DatabaseConfig, HardwareConfig
from watering.database import WateringDatabase
from watering.hardware import MockGPIO, WateringController


@pytest.fixture
def temp_db_path() -> Generator[Path]:
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    if path.exists():
        path.unlink()


@pytest.fixture
def database_config(temp_db_path: Path) -> DatabaseConfig:
    """Create database config with temporary database."""
    return DatabaseConfig(path=temp_db_path)


@pytest.fixture
def hardware_config() -> HardwareConfig:
    """Create hardware config for testing."""
    return HardwareConfig(watering_pin=1, ml_per_second=12.5)


@pytest.fixture
def cors_config() -> CorsConfig:
    """Create CORS config for testing."""
    return CorsConfig(allow_all_origins=True)


@pytest.fixture
def config(
    database_config: DatabaseConfig,
    hardware_config: HardwareConfig,
    cors_config: CorsConfig,
) -> Config:
    """Create complete config for testing."""
    return Config(
        hardware=hardware_config,
        database=database_config,
        cors=cors_config,
        default_user="TestUser",
    )


@pytest.fixture
def mock_gpio() -> MockGPIO:
    """Create mock GPIO for testing."""
    gpio = MockGPIO()
    gpio.setup()
    return gpio


@pytest.fixture
def watering_controller(
    hardware_config: HardwareConfig,
    mock_gpio: MockGPIO,
) -> WateringController:
    """Create watering controller with mock GPIO."""
    controller = WateringController(hardware_config, mock_gpio)
    controller.initialize()
    return controller


@pytest.fixture
def database(database_config: DatabaseConfig) -> WateringDatabase:
    """Create database instance for testing."""
    return WateringDatabase(database_config)
