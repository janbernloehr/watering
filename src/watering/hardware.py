"""Hardware control for the watering system."""

import asyncio
from abc import ABC, abstractmethod
from typing import Protocol

from watering.config import HardwareConfig


class GPIOInterface(Protocol):
    """Protocol for GPIO operations."""

    def setup(self) -> None:
        """Initialize GPIO."""
        ...

    def set_output(self, pin: int) -> None:
        """Set pin as output."""
        ...

    def write_high(self, pin: int) -> None:
        """Write HIGH to pin."""
        ...

    def write_low(self, pin: int) -> None:
        """Write LOW to pin."""
        ...


class BaseGPIO(ABC):
    """Base class for GPIO implementations."""

    @abstractmethod
    def setup(self) -> None:
        """Initialize GPIO."""

    @abstractmethod
    def set_output(self, pin: int) -> None:
        """Set pin as output."""

    @abstractmethod
    def write_high(self, pin: int) -> None:
        """Write HIGH to pin."""

    @abstractmethod
    def write_low(self, pin: int) -> None:
        """Write LOW to pin."""


class MockGPIO(BaseGPIO):
    """Mock GPIO for testing and development."""

    def __init__(self) -> None:
        """Initialize mock GPIO state."""
        self._pins: dict[int, bool] = {}
        self._output_pins: set[int] = set()

    def setup(self) -> None:
        """Initialize mock GPIO."""
        self._pins.clear()
        self._output_pins.clear()

    def set_output(self, pin: int) -> None:
        """Set pin as output."""
        self._output_pins.add(pin)
        self._pins[pin] = False

    def write_high(self, pin: int) -> None:
        """Write HIGH to pin."""
        self._pins[pin] = True

    def write_low(self, pin: int) -> None:
        """Write LOW to pin."""
        self._pins[pin] = False


class RpiGPIO(BaseGPIO):
    """Raspberry Pi GPIO using rpi-lgpio."""

    OUTPUT = 1
    HIGH = 1
    LOW = 0

    def __init__(self) -> None:
        """Initialize RPi GPIO."""
        self._gpio: object | None = None

    def setup(self) -> None:
        """Initialize GPIO using BCM mode."""
        try:
            from RPi import GPIO  # noqa: PLC0415  # ty: ignore[unresolved-import]

            GPIO.setmode(GPIO.BCM)
            self._gpio = GPIO
        except ImportError:
            msg = "RPi.GPIO not available. Use MockGPIO for testing."
            raise RuntimeError(msg) from None

    def set_output(self, pin: int) -> None:
        """Set pin as output."""
        if self._gpio:
            self._gpio.setup(pin, self.OUTPUT)  # type: ignore[union-attr]

    def write_high(self, pin: int) -> None:
        """Write HIGH to pin."""
        if self._gpio:
            self._gpio.output(pin, self.HIGH)  # type: ignore[union-attr]

    def write_low(self, pin: int) -> None:
        """Write LOW to pin."""
        if self._gpio:
            self._gpio.output(pin, self.LOW)  # type: ignore[union-attr]


def create_gpio(*, use_mock: bool = False) -> BaseGPIO:
    """Create appropriate GPIO implementation."""
    if use_mock:
        return MockGPIO()
    try:
        gpio = RpiGPIO()
        gpio.setup()
    except RuntimeError:
        return MockGPIO()
    else:
        return gpio


class WateringController:
    """Controller for the watering pump."""

    def __init__(self, config: HardwareConfig, gpio: GPIOInterface) -> None:
        """Initialize the watering controller."""
        self._config = config
        self._gpio = gpio
        self._initialized = False

    def initialize(self) -> None:
        """Initialize hardware for watering."""
        self._gpio.setup()
        self._gpio.set_output(self._config.watering_pin)
        self._gpio.write_low(self._config.watering_pin)
        self._initialized = True

    async def water(self, volume_ml: int) -> float:
        """
        Activate pump for the specified volume.

        Args:
            volume_ml: Volume of water in milliliters.

        Returns:
            Duration in seconds that the pump ran.
        """
        if not self._initialized:
            self.initialize()

        duration = volume_ml / self._config.ml_per_second

        self._gpio.write_high(self._config.watering_pin)
        try:
            await asyncio.sleep(duration)
        finally:
            self._gpio.write_low(self._config.watering_pin)

        return duration
