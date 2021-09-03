#!/usr/bin/env python3
import requests
import json
import time
import RPi.GPIO as GPIO

# Set GPIO mode
GPIO.setmode(GPIO.BOARD)

# This is to stop RPi.GPIO complaining about GPIO header ports being left on when the script exits
GPIO.setwarnings(False)

# Set LED locations and GPIO channels
led_red = [19, 26]
GPIO.setup(led_red, GPIO.OUT)

led_amber = [21, 24]
GPIO.setup(led_amber, GPIO.OUT)

led_green = [23, 22]
GPIO.setup(led_green, GPIO.OUT)

# Load some variables
apiKey = ""
siteId = ""
alertHigh = 25
alertLow = 15
priceRes = "30"

# Set the URL for the Amber Electric API
apiUrl = (
    f"https://api.amber.com.au/v1/sites/{siteId}/prices/current?resolution={priceRes}"
)

# Set the start time of the script
start_time = time.time()

# Get current price data from the API and parse the JSON
apiResponse = requests.get(
    apiUrl,
    headers={"accept": "application/json", "Authorization": f"Bearer {apiKey}"},
)
priceDataApi = json.loads(apiResponse.text)

# Set variables
currentPrice = float(priceDataApi[0]["perKwh"])
currentPrice2 = "{:.2f}".format(currentPrice)

# Print last price
print("Current price:", currentPrice)

# Turn off all LEDs
GPIO.output(led_red, GPIO.LOW)
GPIO.output(led_amber, GPIO.LOW)
GPIO.output(led_green, GPIO.LOW)

# High price (red LED)
if currentPrice > alertHigh:
    print("Setting red LED...")
    GPIO.output(led_red, GPIO.HIGH)

# Low price (green LED)
if currentPrice < alertLow:
    print("Setting green LED...")
    GPIO.output(led_green, GPIO.HIGH)

# Return to normal (yellow LED)
if currentPrice >= alertLow and currentPrice <= alertHigh:
    print("Setting amber LED...")
    GPIO.output(led_amber, GPIO.HIGH)
