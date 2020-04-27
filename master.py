from time import sleep
import subprocess
import adafruit_ssd1306
from board import SCL, SDA
import board
import digitalio
import busio
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import neopixel
import Adafruit_ADS1x15

# -------------------------------------------------------
#                      NeoPixels
# -------------------------------------------------------
# LED strip configuration:
LED_COUNT      = 50       # Number of LED pixels
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 35     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

colors ={"RED":5,
         "ORANGE":20,
         "YELLOW":28,
         "GREEN":54,
         "LIGHTBLUE":120,
         "BLUE":136,
         "DARKBLUE":145,
         "PURPLE":192,
         "OFF":-1}
# Create NeoPixel object with appropriate configuration.
strip = neopixel.NeoPixel(board.D18, LED_COUNT)
# Intialize the library (must be called once before other functions).
# strip.begin()

# -------------------------------------------------------
# ADS1015 - 4 channel I2C ADC
# -------------------------------------------------------
adc = Adafruit_ADS1x15.ADS1015()
pot_vals = [0.0, 0.0, 0.0, 0.0]
last_pot_vals = [0.0, 0.0, 0.0, 0.0]

# -------------------------------------------------------
# Switches and buttons
# -------------------------------------------------------

neop_button = digitalio.DigitalInOut(board.D23)
air_assist_button = digitalio.DigitalInOut(board.D24)
laser_pointer_button = digitalio.DigitalInOut(board.D25)
neop_button.direction = digitalio.Direction.INPUT
air_assist_button.direction = digitalio.Direction.INPUT
laser_pointer_button.direction = digitalio.Direction.INPUT
# -------------------------------------------------------
# for the OLED Display
# -------------------------------------------------------
# Raspberry Pi pin configuration:
i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
disp.fill(0)
disp.show()
"""
RST = None     # on the PiOLED this pin isnt used

# 128x32 display with hardware I2C:
i2c = busio.I2C(SCL, SDA)
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
# Initialize library.
disp.begin()
# Clear display.
# Clear display.
disp.clear()
disp.display()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
"""
image = Image.new('1', (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
disPx = 0
# Load default font.
# font = ImageFont.load_default()
# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
size3 = 10
size2 = 15
size1 = 20
sm_font = ImageFont.truetype('/home/pi/stft-pedal/prototype/hardware/font.ttf', size3)
m_font = ImageFont.truetype('/home/pi/stft-pedal/prototype/hardware/font.ttf', size2)
lg_font = ImageFont.truetype('/home/pi/stft-pedal/prototype/hardware/font.ttf', size1)

# -------------------------------------------------------
# Functions
# -------------------------------------------------------
def readPots():
    # Main program loop.
    # Read all the ADC channel values in a list.
    # get the pot values from the last two input
    for i in range(4):
        last_pot_vals[i] = pot_vals[i]
        pot_vals[i] = adc.read_adc(i, gain=1) / 4096

def readButtons():
    last_but_vals = but_vals;
    for i in range(3):
        but_vals[i] = buttons[i].value


def wheel(pos):
    """generate rainbow colors across 0-255 positions."""
    if pos == -1:
        return Color(0,0,0)
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def updateStrips():
    # if the button for the NeoPixels is on then set the color
    # according to the position of a Hue, Saturation, and Brightness pot
    if but_vals[0] == True:
        # color = strip.ColorHSV(pot_vals[0], pot_vals[1], pot_vals[2]);
        strip.fill(pot_vals[0]*255, pot_vals[1]*255, pot_vals[2]*255)
        strip.show()

def boot(t=0.5):
    print("booting system")
    print("||||||||||||||||||||||||||||||||||||||")
    print("3")
    # displayLines("Booting")
    strip.fill(255, 0, 0)
    strip.show()
    sleep(t)
    print("2")
    strip.fill(255, 125, 0)
    strip.show()
    sleep(t)
    print("1")
    strip.fill(255, 255, 0)
    strip.show()
    sleep(t)
    print("0")
    strip.fill(0, 255, 0)
    strip.show()

def mainLoop(system):
    readPots()
    readButtons();
    updateStrips();

if __name__ == "__main__":
    boot()
    while True:
        mainLoop(system)
