from time import sleep
import subprocess
import Adafruit_SSD1306
import Adafruit_GPIO.SPI as SPI
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import neopixel
from neopixel import Color
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

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
# make the LED Red for 1 second
# Create NeoPixel object with appropriate configuration.
strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                          LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

# -------------------------------------------------------
# ADS1015 - 4 channel I2C ADC
# -------------------------------------------------------
adc = Adafruit_ASD1x15.ADS1015()
pot_vals = [0.0, 0.0, 0.0, 0.0]
last_pot_vals = [0.0, 0.0, 0.0, 0.0]

# -------------------------------------------------------
# Switches
# -------------------------------------------------------
but_pins = [25, 24, 23]
but_vals = [0, 0, 0]
last_but_vals = [0, 0, 0]

# -------------------------------------------------------
# for the OLED Display
# -------------------------------------------------------
# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x32 display with hardware I2C:
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
        but_vals[i] = gpio.input(but_pins[i]


def printChanges():
    """
    this function will print any changes in the values of the sensors
    it will only print when a change occurs instead of constantly printing
    if you want to constantly print please use the "printsensorvals" function declaired above
    """
    for i, val in enumerate(st_but_vals):
        if val != last_st_but_vals[i]:
            print("stompbutton {}: {}".format(i, val))
    for i, val in enumerate(pot_vals):
        if val != last_pot_vals[i]:
            print("pot {}: {}".format(i, val))
    for i, val in enumerate(system.enc_vals):
        if val != system.last_enc_vals[i]:
            print("enc {}: {}".format(i, val))
    if mode_switch_val !=  last_mode_switch_val:
        print("mode switch: ", mode_switch_val)

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

def setStatusColor(m, b, s=0):
    # print("setStatusColor : ", m)
    if m == "AM":
        system.status_color = wheel(colors['GREEN'])
    elif m == "FM":
        if s == 2:
            system.status_color = wheel(colors['BLUE'])
        if s == 0:
            system.status_color = wheel(colors['LIGHTBLUE'])
        if s == 1:
            system.status_color = wheel(colors['DARKBLUE'])
    elif m == "SPEC-MIX":
        system.status_color = wheel(colors['YELLOW'])
    elif m == "SPEC-MATCH":
        system.status_color = wheel(colors['ORANGE'])
    elif m == "REPITCH":
        system.status_color = wheel(colors['PURPLE'])
    elif m == "PHYS-MOD":
        system.status_color = wheel(colors['RED'])
    setStatusLED(system.status_color, b)

def sendOscOnChanges(system):
    #  gain
    thresh = 0.02
    if abs(pot_vals[0] - system.gain) > thresh:
        system.gain = pot_vals[0]
        if system.gain > 0.99:
            displayLines('out gain 100%', 255)
        else:
            displayLines('out gain ' + str(system.gain*100)[:2] + "%", 255)
        sendOutputGain(system.gain)
        print("sent gain adjustment : ", system.gain)

    # wet/dry
    if abs(pot_vals[1] - system.wet) > thresh:
        system.wet = pot_vals[1]
        if system.wet > 0.99:
            displayLines("dry gain 100% ", 255)
        else:
            displayLines("dry gain  " + str(system.wet * 100)[:2] + "%", 255)
        sendWetDryGain(system.wet)
        print("wet/dry adjustment : ", system.wet)

    # change synthesis mode (3 pos switch)
    global mode_switch_val
    if mode_switch_val != last_mode_switch_val:
        sendSwitchEvent(mode_switch_val)
        setStatusColor(system.mode, system.bypass, mode_switch_val)
        print("switch event osc sent : ", mode_switch_val)

    # encoder 1-3 value
    # contextual to the mode
    # sent  when encoder button pressed
    enc = encoders.Encoders.getInstance(mcp1, mcp2)
    for i, but in enumerate(enc.but_val):
        # if the button was released
        if but == 0 and enc.last_but_val[i] == 1:
            if enc.type[i] == 'continious':
                if system.enc_vals[i] != enc.val[i]:
                    system.enc_vals[i] = enc.val[i]
                sendEncVal(i, enc.val[i])
                displayEncoderChange(i, 255)
                print("Cont encoder {} has been updated to {}".format(i, system.enc_vals[i]))
            elif enc.type[i] == 'discrete':
                if system.enc_vals[i] != enc.val[i]:
                    system.enc_vals[i] = enc.val[i]
                # if we are in repitch mode
                if "pitch" in system.mode.lower():
                    displayEncoderChange(i, 255)
                    sendEncVal(i, enc.val[i])
                    print("repitch (string) - Dis encoder {} has been updated to {}".format(i, enc.val[i]))
                elif type(enc.d_val[i][enc.val[i]]) == str:
                    try:
                        val = float(enc.d_val[i][enc.val[i]])
                        displayEncoderChange(i, 255)
                        sendEncVal(i, val)
                        print("(string) try - Dis encoder {} has been updated to {}".format(i, val))
                    except Exception as e:
                        sendEncVal(i, enc.val[i])
                        displayEncoderChange(i, 255)
                        print("(string) except - Dis encoder {} has been updated to {}  {}".format(i, system.enc_vals[i], enc.val[i]))
                else:
                    sendEncVal(i, enc.d_val[i][enc.val[i]])
                    displayEncoderChange(i, 255)
                    print("(int) Dis encoder {} has been updated to {}".format(i, system.enc_vals[i]))

    # stomp buttons (bypass)
    for i, val in enumerate(st_but_vals):
        # if the stomp button was triggered
        if val != last_st_but_vals[i]:
            sendStompEvent(i)
            print("stompbutton {} has been stomped".format(i))

def setStripColor(color):
    for i in range(50):
        strip.setPixelColor(i, color)
    strip.show()

def updateStrips():
    # if the button for the NeoPixels is on then set the color
    # according to the position of a Hue, Saturation, and Brightness pot
    if but_vals[0] == True:
        color = strip.ColorHSV(pot_vals[0], pot_vals[1], pot_vals[2]);
        setStripColor(color);

def boot(t=0.5):
    print("booting system")
    print("||||||||||||||||||||||||||||||||||||||")
    print("3")
    displayLines("Booting")
    setStripColor(wheel(colors['RED']),1)
    strip.show()
    sleep(t)
    print("2")
    setStripColor(wheel(colors['ORANGE']),1)
    strip.show()
    sleep(t)
    print("1")
    setStripColor(wheel(colors['YELLOW']),1)
    strip.show()
    sleep(t)
    print("0")
    setStripColor(wheel(colors['GREEN']),1)
    strip.show()

def mainLoop(system):
    readPots()
    readButtons();
    updateStrips();

if __name__ == "__main__":
    while True:
        mainLoop(system)
