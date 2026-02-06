"""Tests for configuration module."""

from pathlib import Path

from watering.config import (
    Config,
    CorsConfig,
    DatabaseConfig,
    HardwareConfig,
    get_config,
)


class TestHardwareConfig:
    """Tests for HardwareConfig."""

    def test_defaults(self):
        """Test default values."""
        config = HardwareConfig()
        assert config.watering_pin == 1
        assert config.ml_per_second == 12.5

    def test_custom_values(self):
        """Test custom values."""
        config = HardwareConfig(watering_pin=5, ml_per_second=10.0)
        assert config.watering_pin == 5
        assert config.ml_per_second == 10.0

    def test_immutable(self):
        """Test that config is immutable."""
        config = HardwareConfig()
        try:
            config.watering_pin = 5  # type: ignore[misc]
            raise AssertionError("Should have raised")
        except AttributeError:
            pass


class TestDatabaseConfig:
    """Tests for DatabaseConfig."""

    def test_defaults(self):
        """Test default values."""
        config = DatabaseConfig()
        assert config.path == Path("mydatabase.db")

    def test_connection_string(self):
        """Test connection string generation."""
        config = DatabaseConfig(path=Path("/tmp/test.db"))
        assert config.connection_string == "sqlite:////tmp/test.db"


class TestCorsConfig:
    """Tests for CorsConfig."""

    def test_defaults(self):
        """Test default values."""
        config = CorsConfig()
        assert config.allow_all_origins is True
        assert config.allowed_origins == ()

    def test_specific_origins(self):
        """Test specific origins configuration."""
        config = CorsConfig(
            allow_all_origins=False,
            allowed_origins=("http://localhost:3000", "http://example.com"),
        )
        assert config.allow_all_origins is False
        assert len(config.allowed_origins) == 2


class TestConfig:
    """Tests for main Config."""

    def test_defaults(self):
        """Test default values."""
        config = Config()
        assert isinstance(config.hardware, HardwareConfig)
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.cors, CorsConfig)
        assert config.default_user == "Jan"


class TestGetConfig:
    """Tests for get_config function."""

    def test_returns_config(self):
        """Test that get_config returns a Config instance."""
        config = get_config()
        assert isinstance(config, Config)
