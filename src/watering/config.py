"""Configuration management for the watering system."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class HardwareConfig:
    """Hardware-related configuration."""

    watering_pin: int = 1
    ml_per_second: float = 12.5  # 250ml per 20s = 12.5 ml/s


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    """Database configuration."""

    path: Path = field(default_factory=lambda: Path("mydatabase.db"))

    @property
    def connection_string(self) -> str:
        """Get SQLite connection string."""
        return f"sqlite:///{self.path}"


@dataclass(frozen=True, slots=True)
class CorsConfig:
    """CORS configuration."""

    allow_all_origins: bool = True
    allowed_origins: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Config:
    """Main application configuration."""

    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cors: CorsConfig = field(default_factory=CorsConfig)
    default_user: str = "Jan"


def get_config() -> Config:
    """Get the application configuration."""
    return Config()
