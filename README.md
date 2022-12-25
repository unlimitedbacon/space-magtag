# space-magtag
A fridge magnet which shows upcoming rocket launches

![DSC03398_v2](https://user-images.githubusercontent.com/3131268/209483258-700dd06e-7e00-4801-956f-e4ff5e19793a.JPG)

Uses the [Adafruit MagTag](https://www.adafruit.com/product/4800), an ESP32 based board with an E-Ink display.
Based on the original [SpaceX Launch Display](https://learn.adafruit.com/spacex-next-launch-display-with-adafruit-magtag/overview) project by Adafruit.

## Parts
* [Adafruit MagTag](https://www.adafruit.com/product/4800)
* [Magnet Feet](https://www.adafruit.com/product/4631)
* [Battery](https://www.adafruit.com/product/4236)

## Instructions
1. [Install CircuitPython on your MagTag](https://circuitpython.org/board/adafruit_magtag_2.9_grayscale/). I used version 7.3.3.
2. Copy all files here to the CIRCUITPY drive.
3. Enter your WiFi SSID and password in `secrets.py`.
