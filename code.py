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
from adafruit_magtag.magtag import MagTag
from adafruit_magtag.magtag import Peripherals
from adafruit_datetime import datetime
from utimezone.utimezone import Timezone
from utimezone.utzlist import America_Pacific

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
          "Aug", "Sep", "Oct", "Nov", "Dec"]
USE_24HR_TIME = True
# in seconds, we can refresh about 100 times on a battery
TIME_BETWEEN_REFRESHES = 60 * 60  # once a day delay

# Set up data location and fields
DATA_SOURCE = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?search=SpaceX"
NAME_LOCATION = ['results',0,'name']
DATE_LOCATION = ['results',0,'net']
PAD_LOCATION = ['results',0,'pad','name']
DETAIL_LOCATION = ['results',0,'mission','description']

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
    return val3[0:188]

# Set up the MagTag with the JSON data parameters
magtag = MagTag(
    url=DATA_SOURCE,
    json_path=(NAME_LOCATION, DATE_LOCATION, PAD_LOCATION, DETAIL_LOCATION)
)

magtag.set_background('spacex.bmp')

# Display heading text below with formatting
magtag.add_text(
    text_font="/fonts/Lato-Bold-ltd-25.bdf",
    text_position=(10, 15),
    is_data=False
)

magtag.set_text("Next SpaceX Launch",
    0,
    False
)

# Display battery voltage
magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(264,120),
    is_data=False
)

magtag.set_text(
    "{:.2f}v".format(magtag.peripherals.battery),
    1,
    False
)

# Formatting for the mission text
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 38),
    text_transform=mission_transform
)

# Formatting for the launch time text
magtag.add_text(
    text_font="/fonts/Arial-12.bdf",
    text_position=(10, 58),
    text_transform=time_transform
)

# Formatting for launch pad
magtag.add_text(
    text_font="/fonts/Arial-12.bdf",
    text_position=(130, 58)
)

# Formatting for the details text
magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(10, 94),
    line_spacing=0.8,
    text_wrap=47,     # wrap text at this count
    text_transform=details_transform
)

status_led = digitalio.DigitalInOut(board.D13)
status_led.direction = digitalio.Direction.OUTPUT
status_led.value = False

wifi_status = False

try:
    # Have the MagTag connect to the internet
    magtag.network.connect()
    wifi_status = True
except (ValueError, RuntimeError, ConnectionError, OSError) as e:
    print("WiFi connection failed: ", e)

sprite_sheet, palette = adafruit_imageload.load(
    '/sprites.bmp',
    bitmap=displayio.Bitmap,
    palette=displayio.Palette
)

battery = displayio.TileGrid(
    sprite_sheet,
    pixel_shader=palette,
    width=1,
    height=1,
    tile_width=12,
    tile_height=12,
    default_tile=0
)

signal = displayio.TileGrid(
    sprite_sheet,
    pixel_shader=palette,
    width=1,
    height=1,
    tile_width=12,
    tile_height=12,
    default_tile=1
)

if not wifi_status:
    signal[0] = 2

status_group = displayio.Group()
status_group.append(battery)
status_group.append(signal)
battery.x = 250
battery.y = 116
signal.x = 238
signal.y = 117

magtag.splash.append(status_group)

try:
    # This statement gets the JSON data and displays it automagically
    value = magtag.fetch()
    print("API Response: ", value)
except (ValueError, RuntimeError, ConnectionError, OSError) as e:
    print("Error fetching data: ", e)

# wait 2 seconds for display to complete
time.sleep(2)
magtag.exit_and_deep_sleep(TIME_BETWEEN_REFRESHES)
