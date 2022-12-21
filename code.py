# SPDX-FileCopyrightText: 2020 Anne Barela for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# SpaceX Launch Display, by Anne Barela November 2020
# MIT License - for Adafruit Industries LLC
# See https://lldev.thespacedevs.com/docs/ for API info

import board
import digitalio
import displayio
import rtc
import time
import wifi
import socketpool
import adafruit_ntp
import adafruit_requests as requests
from adafruit_datetime import datetime, timedelta
from adafruit_fakerequests import Fake_Requests
from adafruit_magtag.magtag import MagTag
from adafruit_magtag.magtag import Peripherals
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.solid import Solid

import ui
import music


# CONFIGURATION
# =============

COUNTDOWN_LIGHTS = True
COUNTDOWN_MUSIC  = True
DEV_MODE = False
TIME_BETWEEN_REFRESHES = 60 * 60  # Seconds

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


# HELPER FUNCTIONS
# ================

class BatteryError(Exception):
    def __str__(self):
        return "The battery voltage is too low. Please charge the battery and press the RESET button."


def error_and_sleep(title, ex, halt=False):
    display_group = displayio.Group()
    status_bar = ui.StatusBar(fonts, inverted=True)
    status_bar.update(magtag)
    message = ui.ErrorMessage(fonts, title, ex)
    display_group.append(message.display_group)
    display_group.append(status_bar.display_group)
    magtag.display.show(display_group)
    magtag.display.refresh()

    # Sleep after waiting 2 seconds for display to complete
    print(":: Sleeping")
    time.sleep(2)
    if halt:
        magtag.exit_and_deep_sleep(999999)
    else:
        magtag.exit_and_deep_sleep(TIME_BETWEEN_REFRESHES)


def countdown(launch_time):
    if not COUNTDOWN_LIGHTS:
        return

    print(":: Beginning Countdown")

    frame_time = 1.0/100
    comet1 = Comet(magtag.peripherals.neopixels, speed=0.1, color=(0,128,255), tail_length=3, bounce=True)
    comet2 = Comet(magtag.peripherals.neopixels, speed=0.05, color=(128,0,255), tail_length=3, bounce=True)
    blink = Blink(magtag.peripherals.neopixels, speed=0.5, color=(255,0,0))
    solid = Solid(magtag.peripherals.neopixels, color=(255,128,0))

    t_minus = launch_time - datetime.now()
    while True:
        if t_minus > timedelta(seconds=60):
            comet1.animate()
        elif t_minus > timedelta(seconds=10):
            comet2.animate()
        elif t_minus > timedelta(seconds=0):
            blink.animate()
        else:
            print(":: LAUNCH")
            solid.animate()
            if COUNTDOWN_MUSIC:
                #music.play_music(magtag, music.starwars)
                #music.play_music(magtag, music.close_encounters)
                music.play_music(magtag, music.startrek)
                #music.play_music(magtag, music.indiana)
                #music.play_music(magtag, music.bttf)
                #music.play_music(magtag, music.swbattle)
                #music.play_music(magtag, music.valkyries)
                #music.play_music(magtag, music.portal)
                #music.play_tank(magtag)
            time.sleep(5)
            break

        time.sleep(frame_time)
        t_minus = launch_time - datetime.now()


# MAIN CODE
# =========

# Initialize things
print()
print("MagTag Space Launch Tracker")
print("===========================")
print()
print(":: Starting")
magtag = MagTag()

#countdown(datetime.now() + timedelta(seconds=70))

# Disable red LED to save power
status_led = digitalio.DigitalInOut(board.D13)
status_led.direction = digitalio.Direction.OUTPUT
status_led.value = False

# Load fonts
fonts = ui.Fonts()

# Build display layers
print(":: Building UI")
info_view = ui.InfoView(fonts)
status_bar = ui.StatusBar(fonts)

# Check battery level
if magtag.peripherals.battery < 3.2:
    error_and_sleep("Battery Discharged", BatteryError(), halt=True)

# Connect to network
print(":: Connecting to WiFi")
try:
    magtag.network.connect()
except Exception as e:
    print("WiFi error: ", e)
    error_and_sleep("WiFi Error", e)
    
# Get the current time if the clock isn't already set
try:
    if time.localtime().tm_year < 2020:
        # Important: This sets time.localtime() to UTC
        print(":: Syncing clock")
        pool = socketpool.SocketPool(wifi.radio)
        ntp = adafruit_ntp.NTP(pool, tz_offset=0)
        rtc.RTC().datetime = ntp.datetime
except Exception as e:
    print("Error syncing clock: ", e)
    error_and_sleep("Error Getting Time", e)


# Fetch data
print(":: Fetching data")
success = False
retries = 0
time_to_wakeup = TIME_BETWEEN_REFRESHES

while not success and retries < 3:
    try:
        launches = []
        for term in search_terms:
            print("   - "+term)
            #response = Fake_Requests("test_data.json")
            response = magtag.network.fetch(DATA_URL+term)
            print()
            #print("API Response: ", response.headers)
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
        launch_time = datetime.fromisoformat(launch['net'][:19])
        info_view.update(launch)

    except Exception as e:
        retries += 1
        print("Error fetching data: ", e)
        if retries >= 3:
            error_and_sleep("Error Accessing API", e)

# Update status bar
status_bar.update(magtag)

# Display things
print(":: Displaying")
display_group = displayio.Group()
display_group.append(info_view.display_group)
display_group.append(status_bar.display_group)

magtag.display.show(display_group)
magtag.display.refresh()

# Set wakup timer early if launch is upcoming before next refresh
ctime = datetime.now()    # Actually UTC
#launch_time = ctime + timedelta(minutes=1.5)
diff = launch_time - ctime
refresh_time = timedelta(seconds=TIME_BETWEEN_REFRESHES)
countdown_start = timedelta(minutes=15)
print(":: Time to launch:", diff)
if diff < refresh_time and diff > countdown_start:
    time_to_wakeup = (diff - countdown_start).seconds
elif diff <= countdown_start:
    countdown(launch_time)

# Sleep after waiting 2 seconds for display to complete
print(":: Sleeping for {} seconds".format(time_to_wakeup))
time.sleep(2)
magtag.exit_and_deep_sleep(time_to_wakeup)
