# SPDX-FileCopyrightText: 2020 Anne Barela for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# SpaceX Launch Display, by Anne Barela November 2020
# MIT License - for Adafruit Industries LLC
# See https://github.com/r-spacex/SpaceX-API for API info

import board
import digitalio
import displayio
import time
import terminalio
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_pixels
from adafruit_fakerequests import Fake_Requests
from adafruit_magtag.magtag import MagTag
from adafruit_magtag.magtag import Peripherals
from adafruit_datetime import datetime
from utimezone.utimezone import Timezone
from utimezone.utzlist import America_Pacific

# Configuration
DEV_MODE = True
USE_24HR_TIME = True
TIME_BETWEEN_REFRESHES = 60 * 60  # Seconds

# Set up data location and fields
if DEV_MODE:
    DATA_URL = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?search=SpaceX"
else:
    DATA_URL = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?search=SpaceX"

NAME_PATH = ['results',0,'name']
DATE_PATH = ['results',0,'net']
PAD_PATH = ['results',0,'pad','name']
DETAIL_PATH = ['results',0,'mission','description']

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
          "Aug", "Sep", "Oct", "Nov", "Dec"]

# These functions take the JSON data keys and does checks to determine
#   how to display the data. They're used in the add_text blocks below

def mission_transform(val):
    if val == None:
        val = "Unavailable"
    return val

def time_transform(val2):
    if val2 == None:
        return "When: Unavailable"
    ldate = datetime.fromisoformat(val2[:19])
    local = America_Pacific.toLocal(ldate)

    if USE_24HR_TIME:
        timestring = "%02d:%02d" % (local.hour, local.minute)
    elif hour > 12:
        timestring = "%d:%02d pm" % (local.hour-12, local.minute)
    else:
        timestring = "%d:%02d am" % (local.hour, local.minute)

    return "%s %d at %s" % (months[local.month-1], local.day, timestring)

def details_transform(val3):
    if val3 == None or not len(val3):
        return "Details: To Be Determined"
    return "\n".join(wrap_text_to_pixels(val3, 276, font_small)[:4])

# Initialize things
print(":: Starting")
magtag = MagTag()

status_led = digitalio.DigitalInOut(board.D13)
status_led.direction = digitalio.Direction.OUTPUT
status_led.value = False

# Load fonts
print(":: Loading fonts")
font_large = bitmap_font.load_font("/fonts/Lato-Bold-ltd-25.bdf")
font_medium_bold = bitmap_font.load_font("/fonts/Arial-Bold-12.pcf")
font_medium = bitmap_font.load_font("/fonts/Arial-12.bdf")
font_small = terminalio.FONT

# Build display layers
print(":: Building UI")
# Background
bg_bmp = displayio.OnDiskBitmap("spacex.bmp")
bg_tile = displayio.TileGrid(bg_bmp, pixel_shader=bg_bmp.pixel_shader)
bg_group = displayio.Group()
bg_group.append(bg_tile)

# Launch information text
launch_info_group = displayio.Group()
header_label = label.Label(
    font_large,
    color=0x000000,
    x=10, y=15,
    text="Next SpaceX Launch",
)
mission_label = label.Label(
    font_medium_bold,
    color=0x000000,
    x=10, y=38,
    text="Mission Name"
)
time_label = label.Label(
    font_medium,
    color=0x000000,
    x=10, y=58,
    text="Time"
)
pad_label = label.Label(
    font_small,
    color=0x000000,
    x=130, y=58,
    text="Launch Pad"
)
details_label = label.Label(
    font_small,
    color=0x000000,
    x=10, y=74,
    text="Details",
    anchor_poiint=(0,0),
    line_spacing=0.8,
    text_wrap=47,
)
launch_info_group.append(header_label)
launch_info_group.append(mission_label)
launch_info_group.append(time_label)
launch_info_group.append(pad_label)
launch_info_group.append(details_label)

# Status bar
status_bar_group = displayio.Group()
sprite_sheet, palette = adafruit_imageload.load(
    '/sprites.bmp',
    bitmap=displayio.Bitmap,
    palette=displayio.Palette
)
signal_icon = displayio.TileGrid(
    sprite_sheet,
    pixel_shader=palette,
    width=1,
    height=1,
    tile_width=12,
    tile_height=12,
    default_tile=2,
    x=238, y=117,
)
battery_icon = displayio.TileGrid(
    sprite_sheet,
    pixel_shader=palette,
    width=1,
    height=1,
    tile_width=12,
    tile_height=12,
    default_tile=0,
    x=250, y=116,
)
battery_label = label.Label(
    font_small,
    color=0x000000,
    x=264, y=120,
    text="{:.2f}v".format(magtag.peripherals.battery),
)
status_bar_group.append(signal_icon)
status_bar_group.append(battery_icon)
status_bar_group.append(battery_label)

# Connect to network
#print(":: Connecting to WiFi")
#try:
#    # Have the MagTag connect to the internet
#    magtag.network.connect()
#except (ValueError, RuntimeError, ConnectionError, OSError) as e:
#    print("WiFi connection failed: ", e)
#if magtag.network.is_connected:
#    signal_icon[0] = 1


# Fetch data
print(":: Fetching data")
try:
    #value = magtag.fetch()
    response = Fake_Requests("test_data.json")
    data = response.json()
    #print("API Response: ", response.headers)
except (ValueError, RuntimeError, ConnectionError, OSError) as e:
    print("Error fetching data: ", e)

# Update display objects
print(":: Updating UI")
launch = data['results'][0]
mission_label.text = mission_transform(launch['name'])
time_label.text = time_transform(launch['net'])
pad_label.text = launch['pad']['name']
details_label.text = details_transform(launch['mission']['description'])
print(mission_label.text)
print(time_label.text)
print(pad_label.text)
print(details_label.text)

# Display things
print(":: Displaying")
display_group = displayio.Group()
display_group.append(bg_group)
display_group.append(launch_info_group)
display_group.append(status_bar_group)

magtag.display.show(display_group)
magtag.display.refresh()

# Sleep after waiting 2 seconds for display to complete
print("Sleeping")
time.sleep(2)
magtag.exit_and_deep_sleep(TIME_BETWEEN_REFRESHES)
