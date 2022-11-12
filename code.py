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
import adafruit_requests as requests
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
    DATA_URL = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?search="
else:
    DATA_URL = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?search="

search_terms = ["SpaceX", "NASA"]

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
          "Aug", "Sep", "Oct", "Nov", "Dec"]
status_filters = [ 3, # Success
                   4, # Failure
                   6, # In Flight
                   7, # Partial Failure
]

# These functions take the JSON data keys and does checks to determine
#   how to display the data. They're used in the add_text blocks below

def header_transform(val):
    return "Next {} Launch".format(val)

def mission_transform(val):
    if val == None:
        val = "Unavailable"
    return val

def time_transform(val2):
    if val2 == None:
        return "Unknown"
    ldate = datetime.fromisoformat(val2[:19])
    local = America_Pacific.toLocal(ldate)

    if USE_24HR_TIME:
        timestring = "%02d:%02d" % (local.hour, local.minute)
    elif hour > 12:
        timestring = "%d:%02d pm" % (local.hour-12, local.minute)
    else:
        timestring = "%d:%02d am" % (local.hour, local.minute)

    return "%s %d at %s" % (months[local.month-1], local.day, timestring)

def details_transform(val):
    print(val)
    if val == None or not len(val):
        return "Unavailable"
    return "\n".join(wrap_text_to_pixels(val.replace('\r',''), 280, font_small)[:3])

def pad_transform(val):
    if val == None or not len(val):
        return "Unavailable"
    return val.split(",")[0]

def rocket_transform(val):
    if val  == None or not len(val):
        return "Unavailable"
    return wrap_text_to_pixels(val, 120, font_small)[0]

def status_transform(val):
    if val == None or not len(val):
        return "Unavailable"
    return "Status: " + val

# Initialize things
print(":: Starting")
magtag = MagTag()

status_led = digitalio.DigitalInOut(board.D13)
status_led.direction = digitalio.Direction.OUTPUT
status_led.value = False

# Load fonts
print(":: Loading fonts")
font_large = bitmap_font.load_font("/fonts/Lato-Bold-ltd-25.bdf")
font_large.load_glyphs(range(32,128))   # Cache printable ASCII chars
font_medium_bold = bitmap_font.load_font("/fonts/Arial-Bold-12.pcf")
font_medium_bold.load_glyphs(range(32,128))
font_medium = bitmap_font.load_font("/fonts/Arial-12.bdf")
font_medium.load_glyphs(range(32,128))
font_small = terminalio.FONT

# Build display layers
print(":: Building UI")

# Launch information text
print("   - Info")
launch_info_group = displayio.Group()
header_label = label.Label(
    font_large,
    color=0x000000,
    x=8, y=15,
    text="Next Launch",
)
mission_label = label.Label(
    font_medium_bold,
    color=0x000000,
    x=8, y=38,
    text="Mission Name"
)
time_label = label.Label(
    font_medium,
    color=0x000000,
    x=8, y=57,
    text="Time"
)
pad_label = label.Label(
    font_medium,
    color=0x000000,
    x=135, y=57,
    text="Location"
)
rocket_label = label.Label(
    font_small,
    color=0x000000,
    x=8, y=73,
    text="Rocket",
)
status_label = label.Label(
    font_small,
    color=0x000000,
    x=135, y=73,
    text="Status",
)
details_label = label.Label(
    font_small,
    color=0x000000,
    x=8, y=85,
    text="Details",
    anchor_poiint=(0,0),
    line_spacing=0.8,
    text_wrap=47,
)
launch_info_group.append(header_label)
launch_info_group.append(mission_label)
launch_info_group.append(time_label)
launch_info_group.append(pad_label)
launch_info_group.append(rocket_label)
launch_info_group.append(status_label)
launch_info_group.append(details_label)

# Status bar
print("   - Status")
status_bar_group = displayio.Group()
sprite_sheet, palette = adafruit_imageload.load(
    '/bmp/sprites.bmp',
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
print(":: Connecting to WiFi")
try:
    # Have the MagTag connect to the internet
    magtag.network.connect()
except (ValueError, RuntimeError, ConnectionError, OSError) as e:
    print("WiFi connection failed: ", e)
if magtag.network.is_connected:
    signal_icon[0] = 1

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
        for l in launches:
            print(l['name'])
        sorted_launches = sorted(launches, key=lambda l: l['net'])
        for l in sorted_launches:
            print(l['name'])
        filtered_launches = [x for x in sorted_launches if x['status']['id'] not in status_filters] 
        # Update display objects
        print(":: Updating UI")
        launch = filtered_launches[0]
        # Background
        print("   - Background")
        bg_bmp = displayio.OnDiskBitmap("/bmp/{}.bmp".format(launch['term']))
        bg_tile = displayio.TileGrid(bg_bmp, pixel_shader=bg_bmp.pixel_shader)
        bg_group = displayio.Group()
        bg_group.append(bg_tile)
        header_label.text = header_transform(launch['term'])
        mission_label.text = mission_transform(launch['mission']['name'])
        time_label.text = time_transform(launch['net'])
        pad_label.text = pad_transform(launch['pad']['location']['name'])
        rocket_label.text = rocket_transform(launch['rocket']['configuration']['full_name'])
        status_label.text = status_transform(launch['status']['abbrev'])
        details_label.text = details_transform(launch['mission']['description'])
        print(mission_label.text)
        print(time_label.text)
        print(pad_label.text)
        print(status_label.text)
        print(details_label.text)
    except (ValueError, RuntimeError, ConnectionError, OSError) as e:
        retries += 1
        print("Error fetching data: ", e)

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
