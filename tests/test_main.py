import unittest
from unittest.mock import patch
import sys
import json
from types import ModuleType
import importlib


def build_fakes(price_value):
    # Create a fake GPIO module compatible with RPi.GPIO API used by main.py
    gpio = ModuleType("GPIO")
    gpio.BOARD = "BOARD"
    gpio.OUT = "OUT"
    gpio.HIGH = 1
    gpio.LOW = 0

    # Tracking fields
    gpio._setmode_value = None
    gpio._warnings_value = None
    gpio._setups = []
    gpio._outputs = []
    gpio._states = {}

    def setmode(val):
        gpio._setmode_value = val

    def setwarnings(flag):
        gpio._warnings_value = flag

    def setup(channels, mode):
        if isinstance(channels, (list, tuple)):
            for ch in channels:
                gpio._setups.append((ch, mode))
        else:
            gpio._setups.append((channels, mode))

    def output(channels, value):
        if isinstance(channels, (list, tuple)):
            for ch in channels:
                gpio._outputs.append((ch, value))
                gpio._states[ch] = value
        else:
            gpio._outputs.append((channels, value))
            gpio._states[channels] = value

    gpio.setmode = setmode
    gpio.setwarnings = setwarnings
    gpio.setup = setup
    gpio.output = output

    # Create a fake RPi package exposing the fake GPIO module
    rpi = ModuleType("RPi")
    rpi.GPIO = gpio

    # Create a fake requests module
    requests = ModuleType("requests")

    class Response:
        def __init__(self, text):
            self.text = text

    def get(url, headers=None):
        requests._last_url = url
        requests._last_headers = headers or {}
        # Simulate Amber API response structure
        return Response(json.dumps([{"perKwh": price_value}]))

    requests.get = get
    requests.Response = Response
    requests._last_url = None
    requests._last_headers = None

    return rpi, gpio, requests


def run_main_with_price(price_value):
    rpi, gpio, requests = build_fakes(price_value)
    # Patch sys.modules so that imports inside main() resolve to our fakes
    with patch.dict(
        sys.modules, {"RPi": rpi, "RPi.GPIO": rpi.GPIO, "requests": requests}
    ):
        import main

        # Reload ensures a clean module state each invocation
        importlib.reload(main)
        main.main()
    return gpio, requests


class TestMain(unittest.TestCase):
    def assert_led_states(self, gpio, red, amber, green):
        for pin in [19, 26]:
            self.assertEqual(
                gpio._states.get(pin),
                gpio.HIGH if red else gpio.LOW,
                f"Red pin {pin} state mismatch",
            )
        for pin in [21, 24]:
            self.assertEqual(
                gpio._states.get(pin),
                gpio.HIGH if amber else gpio.LOW,
                f"Amber pin {pin} state mismatch",
            )
        for pin in [23, 22]:
            self.assertEqual(
                gpio._states.get(pin),
                gpio.HIGH if green else gpio.LOW,
                f"Green pin {pin} state mismatch",
            )

    def test_setup_and_api_headers_and_url(self):
        gpio, requests = run_main_with_price(26.0)

        # GPIO mode and warnings
        self.assertEqual(gpio._setmode_value, gpio.BOARD)
        self.assertEqual(gpio._warnings_value, False)

        # GPIO setups include all pins as OUT
        setup_pins = {pin for pin, mode in gpio._setups if mode == gpio.OUT}
        self.assertTrue({19, 26, 21, 24, 23, 22}.issubset(setup_pins))

        # Requests called with expected URL and headers based on defaults in main.py
        self.assertEqual(
            requests._last_url,
            "https://api.amber.com.au/v1/sites//prices/current?resolution=30",
        )
        self.assertEqual(requests._last_headers.get("accept"), "application/json")
        self.assertEqual(requests._last_headers.get("Authorization"), "Bearer ")

    def test_high_price_sets_red_only(self):
        gpio, _ = run_main_with_price(26.0)  # > alertHigh (25)
        self.assert_led_states(gpio, red=True, amber=False, green=False)

    def test_low_price_sets_green_only(self):
        gpio, _ = run_main_with_price(14.9)  # < alertLow (15)
        self.assert_led_states(gpio, red=False, amber=False, green=True)

    def test_mid_price_sets_amber_only(self):
        # Between thresholds
        gpio, _ = run_main_with_price(20.0)
        self.assert_led_states(gpio, red=False, amber=True, green=False)

        # Boundary conditions are inclusive for amber
        gpio, _ = run_main_with_price(15.0)  # == alertLow
        self.assert_led_states(gpio, red=False, amber=True, green=False)

        gpio, _ = run_main_with_price(25.0)  # == alertHigh
        self.assert_led_states(gpio, red=False, amber=True, green=False)


if __name__ == "__main__":
    unittest.main()
