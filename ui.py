import displayio
import terminalio
import time
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_pixels
from adafruit_datetime import datetime
from utimezone.utimezone import Timezone
from utimezone.utzlist import America_Pacific

USE_24HR_TIME = True

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
          "Aug", "Sep", "Oct", "Nov", "Dec"]


class Fonts:
    def __init__(self):
        print(":: Loading Fonts")
        self.large = bitmap_font.load_font("/fonts/Lato-Bold-ltd-25.bdf")
        self.large.load_glyphs(range(32,128))   # Cache printable ASCII chars
        self.medium_bold = bitmap_font.load_font("/fonts/Arial-Bold-12.pcf")
        self.medium_bold.load_glyphs(range(32,128))
        self.medium = bitmap_font.load_font("/fonts/Arial-12.bdf")
        self.medium.load_glyphs(range(32,128))
        self.small = terminalio.FONT


class InfoView:
    def __init__(self, fonts):
        self.__fonts = fonts
        self.display_group = displayio.Group()

        self.bg_group = displayio.Group()

        self.header_label = label.Label(
            fonts.large,
            color=0x000000,
            x=8, y=15,
            text="Next Launch",
        )
        self.mission_label = label.Label(
            fonts.medium_bold,
            color=0x000000,
            x=8, y=38,
            text="Mission Name"
        )
        self.time_label = label.Label(
            fonts.medium,
            color=0x000000,
            x=8, y=57,
            text="Time"
        )
        self.pad_label = label.Label(
            fonts.medium,
            color=0x000000,
            x=135, y=57,
            text="Location"
        )
        self.rocket_label = label.Label(
            fonts.small,
            color=0x000000,
            x=8, y=73,
            text="Rocket",
        )
        self.status_label = label.Label(
            fonts.small,
            color=0x000000,
            x=135, y=73,
            text="Status",
        )
        self.details_label = label.Label(
            fonts.small,
            color=0x000000,
            x=8, y=85,
            text="Details",
            anchor_poiint=(0,0),
            line_spacing=0.8,
            text_wrap=47,
        )
        
        self.display_group.append(self.bg_group)
        self.display_group.append(self.header_label)
        self.display_group.append(self.mission_label)
        self.display_group.append(self.time_label)
        self.display_group.append(self.pad_label)
        self.display_group.append(self.rocket_label)
        self.display_group.append(self.status_label)
        self.display_group.append(self.details_label)

    def update(self, launch):
        # Background image
        bg_bmp = displayio.OnDiskBitmap("/bmp/{}.bmp".format(launch['term']))
        bg_tile = displayio.TileGrid(bg_bmp, pixel_shader=bg_bmp.pixel_shader)
        self.bg_group.append(bg_tile)

        # Text
        self.header_label.text  = self.__header_transform(  launch['term'] )
        self.mission_label.text = self.__mission_transform( launch['mission']['name'] )
        self.time_label.text    = self.__time_transform(    launch['net'] )
        self.pad_label.text     = self.__pad_transform(     launch['pad']['location']['name'] )
        self.rocket_label.text  = self.__rocket_transform(  launch['rocket']['configuration']['full_name'] )
        self.status_label.text  = self.__status_transform(  launch['status']['abbrev'] )
        self.details_label.text = self.__details_transform( launch['mission']['description'] )
        print(self.mission_label.text)
        print(self.time_label.text)
        print(self.pad_label.text)
        print(self.status_label.text)
        print(self.details_label.text)

    def __header_transform(self, val):
        return "Next {} Launch".format(val)

    def __mission_transform(self, val):
        if val == None:
            val = "Unavailable"
        return val

    def __time_transform(self, val2):
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

    def __details_transform(self, val):
        if val == None or not len(val):
            return "Unavailable"
        return "\n".join(wrap_text_to_pixels(val.replace('\r',''), 280, self.__fonts.small)[:3])

    def __pad_transform(self, val):
        if val == None or not len(val):
            return "Unavailable"
        return val.split(",")[0]

    def __rocket_transform(self, val):
        if val  == None or not len(val):
            return "Unavailable"
        return wrap_text_to_pixels(val, 120, self.__fonts.small)[0]

    def __status_transform(self, val):
        if val == None or not len(val):
            return "Unavailable"
        return "Status: " + val


class StatusBar:
    def __init__(self, fonts):
        self.display_group = displayio.Group()
        sprite_sheet, palette = adafruit_imageload.load(
            '/bmp/sprites.bmp',
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        self.signal_icon = displayio.TileGrid(
            sprite_sheet,
            pixel_shader=palette,
            width=1,
            height=1,
            tile_width=12,
            tile_height=12,
            default_tile=2,
            x=238, y=117,
        )
        self.battery_icon = displayio.TileGrid(
            sprite_sheet,
            pixel_shader=palette,
            width=1,
            height=1,
            tile_width=12,
            tile_height=12,
            default_tile=0,
            x=250, y=116,
        )
        self.battery_label = label.Label(
            fonts.small,
            color=0x000000,
            x=264, y=120,
        )
        self.time_label = label.Label(
            fonts.small,
            color=0x000000,
            x=200, y=120
        )
        self.display_group.append(self.signal_icon)
        self.display_group.append(self.battery_icon)
        self.display_group.append(self.battery_label)
        self.display_group.append(self.time_label)

    def update(self, magtag):
        self.battery_label.text = "{:.2f}v".format(magtag.peripherals.battery)
        t = time.localtime()
        self.time_label.text = "{:0>2d}:{:0>2d}".format(t.tm_hour, t.tm_min)

        if magtag.network.is_connected:
            self.signal_icon[0] = 1
        else:
            self.signal_icon[0] = 2

class ErrorMessage:
    def __init__(self, fonts, title, exception):
        self.__fonts = fonts
        self.display_group = displayio.Group()

        self.header1_label = label.Label(
            fonts.large,
            color=0xffffff,
            x=8, y=15,
            text=title,
        )
        self.header2_label = label.Label(
            fonts.medium_bold,
            color=0xffffff,
            x=8, y=38,
            text=type(exception).__name__
        )
        self.details_label = label.Label(
            fonts.small,
            color=0xffffff,
            x=8, y=57,
            text="Details",
            anchor_poiint=(0,0),
            line_spacing=0.8,
            text_wrap=47,
            text=self.__details_transform(str(exception))
        )

        self.display_group.append(self.header1_label)
        self.display_group.append(self.header2_label)
        self.display_group.append(self.details_label)

    def __details_transform(self, val):
        if val == None:
            return ""
        return "\n".join(wrap_text_to_pixels(val.replace('\r',''), 280, self.__fonts.small))
