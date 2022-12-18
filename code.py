# SPDX-FileCopyrightText: 2020 Anne Barela for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# SpaceX Launch Display, by Anne Barela November 2020
# MIT License - for Adafruit Industries LLC
# See https://lldev.thespacedevs.com/docs/ for API info

import board
import digitalio
import displayio
import time
import adafruit_requests as requests
from adafruit_fakerequests import Fake_Requests
from adafruit_magtag.magtag import MagTag
from adafruit_magtag.magtag import Peripherals
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.comet import Comet

import ui
import music

# Configuration
DEV_MODE = False
TIME_BETWEEN_REFRESHES = 60 * 60  # Seconds

# Set up data location and fields
if DEV_MODE:
    DATA_URL = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?search="
else:
    DATA_URL = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?search="

search_terms = ["SpaceX", "NASA"]
status_filters = [ 3, # Success
                   4, # Failure
                   6, # In Flight
                   7, # Partial Failure
]

def error_and_sleep(title, ex):
    message = ui.ErrorMessage(fonts, title, ex)
    magtag.display.show(message.display_group)
    magtag.display.refresh()

    # Sleep after waiting 2 seconds for display to complete
    print(":: Sleeping")
    time.sleep(2)
    magtag.exit_and_deep_sleep(TIME_BETWEEN_REFRESHES)

def countdown():
    #blink = Blink(magtag.peripherals.neopixels, speed=0.5, color=(255,0,0))
    comet = Comet(magtag.peripherals.neopixels, speed=0.1, color=(0,128,255), tail_length=3, bounce=True)
    #comet = RainbowComet(magtag.peripherals.neopixels, speed=0.1, tail_length=3, bounce=True)

    end = time.monotonic()+10
    while time.monotonic() < end:
        comet.animate()


# Initialize things
print(":: Starting")
magtag = MagTag()

#music.play_tank(magtag)
#music.play_music(magtag, music.valkyries)
#music.play_music(magtag, music.swbattle)
#music.play_music(magtag, music.portal)
#countdown()

status_led = digitalio.DigitalInOut(board.D13)
status_led.direction = digitalio.Direction.OUTPUT
status_led.value = False

# Load fonts
fonts = ui.Fonts()

# Build display layers
print(":: Building UI")
info_view = ui.InfoView(fonts)
status_bar = ui.StatusBar(fonts)

# Connect to network
print(":: Connecting to WiFi")
try:
    magtag.network.connect()
except Exception as e:
    print("WiFi error: ", e)
    error_and_sleep("WiFi Error", e)

# Fetch data
print(":: Fetching data")
success = False
retries = 0

while not success and retries < 3:
    try:
        launches = []
        for term in search_terms:
            print("   - "+term)
            #response = Fake_Requests("test_data.json")
            response = magtag.network.fetch(DATA_URL+term)
            print("API Response: ", response.headers)
            data = response.json()
            
            # Save search term with each launch
            for l in data['results']:
                l['term'] = term

            launches += data['results']

        success = True

        # Sort launches by date
        sorted_launches = sorted(launches, key=lambda l: l['net'])

        # Filter launches that already happened
        filtered_launches = [x for x in sorted_launches if x['status']['id'] not in status_filters] 
        for l in filtered_launches:
            print(l['name'])

        # Update display objects
        print(":: Updating UI")
        launch = filtered_launches[0]
        info_view.update(launch)

    except Exception as e:
        retries += 1
        print("Error fetching data: ", e)
        if retries >= 3:
            error_and_sleep("Error Accessing API", e)

status_bar.update(magtag)

# Display things
print(":: Displaying")
display_group = displayio.Group()
display_group.append(info_view.display_group)
display_group.append(status_bar.display_group)

magtag.display.show(display_group)
magtag.display.refresh()

# Sleep after waiting 2 seconds for display to complete
print(":: Sleeping")
time.sleep(2)
magtag.exit_and_deep_sleep(TIME_BETWEEN_REFRESHES)
