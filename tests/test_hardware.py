"""Tests for hardware module."""

import pytest

from watering.config import HardwareConfig
from watering.hardware import MockGPIO, WateringController, create_gpio


class TestMockGPIO:
    """Tests for MockGPIO."""

    def test_setup(self):
        """Test GPIO setup."""
        gpio = MockGPIO()
        gpio.setup()
        assert gpio._pins == {}
        assert gpio._output_pins == set()

    def test_set_output(self):
        """Test setting pin as output."""
        gpio = MockGPIO()
        gpio.setup()
        gpio.set_output(1)

        assert 1 in gpio._output_pins
        assert gpio._pins[1] is False

    def test_write_high_low(self):
        """Test writing high and low to pins."""
        gpio = MockGPIO()
        gpio.setup()
        gpio.set_output(1)

        gpio.write_high(1)
        assert gpio._pins[1] is True

        gpio.write_low(1)
        assert gpio._pins[1] is False


class TestCreateGPIO:
    """Tests for create_gpio function."""

    def test_mock_gpio(self):
        """Test creating mock GPIO."""
        gpio = create_gpio(use_mock=True)
        assert isinstance(gpio, MockGPIO)

    def test_fallback_to_mock(self):
        """Test fallback to mock when RPi.GPIO unavailable."""
        gpio = create_gpio(use_mock=False)
        assert isinstance(gpio, MockGPIO)


class TestWateringController:
    """Tests for WateringController."""

    def test_initialize(self, hardware_config: HardwareConfig, mock_gpio: MockGPIO):
        """Test controller initialization."""
        controller = WateringController(hardware_config, mock_gpio)
        controller.initialize()

        assert controller._initialized
        assert hardware_config.watering_pin in mock_gpio._output_pins

    def test_water(self, watering_controller: WateringController):
        """Test watering operation."""
        duration = watering_controller.water(125)

        assert duration == pytest.approx(10.0, rel=0.1)

    def test_water_auto_initializes(self, hardware_config: HardwareConfig, mock_gpio: MockGPIO):
        """Test that water() auto-initializes if needed."""
        controller = WateringController(hardware_config, mock_gpio)
        assert not controller._initialized

        controller.water(125)
        assert controller._initialized
