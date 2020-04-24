from time import sleep
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import subprocess
import Adafruit_SSD1306
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import neopixel
from neopixel import Color

# -------------- Custom Packages ------------------------
from encoders import encoders
from pwr_button import pwr_button

# -------------------------------------------------------
#                      NeoPixels
# -------------------------------------------------------
# LED strip configuration:
LED_COUNT      = 2       # Number of LED pixels
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
# MSP3008's
# -------------------------------------------------------
# MCP3008 #1:
# encoder #1: 1,2,3
# encoder #2: 4,5,6
# pot #1: 7
# pot #2: 8

# MCP3008 #2:
# encoder #3 1,2,3
# stompbuttons 1-3: 4,5,6
# switch : 7,8

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE0 = 0 # 0
SPI_DEVICE1 = 1 # 0

mcp1 = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE0))
mcp2 = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE1))

# -------------------------------------------------------
# Switches
# -------------------------------------------------------
pwr_but = pwr_button.PowerButton()

last_mode_switch_val = 0
mode_switch_val = 0 # ranges from 0-2
mode_switch_pins = [6,7]

# -------------------------------------------------------
# Potentiometers
# -------------------------------------------------------
pot_vals = [0.0,0.0]
last_pot_vals = [0,0]
pot_pins = [6,7]

# -------------------------------------------------------
# Stompbuttons
# -------------------------------------------------------
# the stomp buttons use the first 3 pins of the first mcp
st_but_vals = [0, 0, 0]
last_st_but_vals = [0, 0, 0]
st_but_pins = [3, 4, 5]


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
def sendOutputGain(gain):
    client.send_message(b"/output/gain", [float(gain)])

def sendWetDryGain(gain):
    client.send_message(b"/wetdry/gain", [float(gain)])

def sendSwitchEvent(value):
    client.send_message(b"/switch", [int(value)])

def sendEncVal(encNum, value):
    client.send_message(b"/encoder", [encNum, float(value)])

def recvContEncoderInfo(encNum, name, minv, maxv, step, start):
    enc = encoders.Encoders.getInstance(mcp1, mcp2)
    enc.setEncoderContInfo(encNum, str(name)[2:-1], minv, maxv, step, start)
    print("received continious encoder info {} {}".format(encNum, name))
    enc.printStats(encNum)

def recvDisEncoderInfo(encNum, name, start, vals):
    enc = encoders.Encoders.getInstance(mcp1, mcp2)
    enc.setEncoderDisInfo(encNum, name, start, vals)
    # print('-'*10)
    # print('discrete encoder value{} {}'.format(type(vals), vals))
    # print('-'*10)

def sendStompEvent(stompNum):
    client.send_message(b"/stomp", [stompNum])

def recvBypassInfo(bypass_state):
    if bypass_state == 0:
        displayLines("BYPASS OFF")
        strip.setBrightness(LED_BRIGHTNESS)
        setStompLED(system.status_color)
        system.bypass = 0
        print("bypass turned off")
    else:
        displayLines("BYPASS ON")
        system.bypass = 1
        setStompLED(Color(0, 10, 0))
        strip.setBrightness(10)
        print("bypass turned on")

def recvDisplayInfo(t1, t2, t3, t4):
    print(" received display message")
    print(t1)
    print(t2)
    print(t3)
    print(t4)

def recvModeInfo(modeName, bypass):
    global mode_switch_val;
    system.mode = str(modeName)[2:-1]
    displayLines(system.mode)
    setStatusColor(system.mode, bypass)
    if system.mode == "PHYSICAL":
        sendSwitchEvent("PM: " + mode_switch_val)
    print("mode message received {}".format(system.mode))
    print("-"*10)

def recvSwitchInfo(value):
    value = str(value)[2:-1]
    print("-------------------------------")
    print("received switch info {}".format(value))
    print("-------------------------------")
    displayLines(value)

def recvShutdownMsg(temp):
    print("shutting down power")
    shut = "sudo shutdown -h now"
    displayLines("SHUTDOWN")
    setStatusLED(wheel(colors['RED']),0)
    sleep(2)
    displayLines("          ")
    strip.setPixelColor(0, wheel(-1))
    strip.setPixelColor(1, wheel(-1))
    strip.show()
    process = subprocess.Popen(shut.split(), stdout=subprocess.PIPE)
    print(process.communicate())

def recvPitchMsg(pitch):
    pitch = str(pitch).split(".")[0] + "."  + str(pitch).split(".")[1][:2]
    displayLines(["Onset Detected", str(pitch)])

def displayLines(strings, fill=0):
    draw.rectangle((0,0,width, height), outline=0, fill=fill)
    lines = 0
    if type(strings) == list:
        for s in strings:
            if s != '':
                lines = lines + 1
    elif type(strings) == str:
        lines = 1

    if lines > 2:
        for i, string in enumerate(strings):
            draw.text((0, top + (i*size3) + 1), " " + str(string), font=sm_font, fill=255-fill)
    elif lines == 2:
        for i, string in enumerate(strings):
            draw.text((0, top + (i*size2) + 1), " " + str(string), font=m_font, fill=255-fill)
    else:
        draw.text((0, top), " " + str(strings), font=lg_font, fill=255-fill)
    disp.image(image)
    disp.display()

def displayEncoderChange(n, fill=0):
    if n >  -1 and n < 3:
        enc = encoders.Encoders.getInstance(mcp1, mcp2)
        if enc.type[n] == 'continious':
            strings = [enc.name[n], str(enc.val[n])[:4]]
            # ,"{} - {} - {}".format(enc.min[n], enc.val[n], enc.max[n])]
            displayLines(strings, fill)
        elif enc.type[n] == 'discrete':
            # print("encoder{} value {}".format(n, enc.val[n]), " ", n)
            if enc.val[n] > -1:
                try:
                    strings = ["{}".format(enc.name[n]),
                            "{}".format(enc.d_val[n][enc.val[n]][-15:])]
                except IndexError:
                    print("index : ", n)
                    print("enc name : ", enc.name[n])
                    print("enc dval : ", enc.d_val[n])
                    print("enc val  : ", enc.val[n])
                    strings = ["{}".format(enc.name[n]),
                            "{}".format(enc.d_val[n][enc.val[n]])]
                displayLines(strings, fill)

def storeCurrentValues():
    """
    Moves all of the current vals to last_vals
    """
    global pwr_val
    global mode_switch_val
    global last_mode_switch_val
    last_mode_switch_val = mode_switch_val
    for i, val in enumerate(pot_vals):
        last_pot_vals[i] = val
    for i, val in enumerate(st_but_vals):
        last_st_but_vals[i] = val

def readMCPs():
    # Main program loop.
    # Read all the ADC channel values in a list.
    # The read_adc function will get the value of the specified channel (0-7).
    ########################################
    # MCP3008 #1:
    ########################################
    # encoder #1: 1,2,3
    # encoder #2: 4,5,6
    # pots: 7, 8


    # get the pot values from the last two input
    for i, pin in enumerate(pot_pins):
        pot_vals[i] = float(mcp1.read_adc(pin))/1023
        if pot_vals[i] < 0.025:
            pot_vals[i] = 0.0
        elif (pot_vals[i] > 0.975):
            pot_vals[i] = 1.0

    ########################################
    # mcp3008 #2:
    ########################################
    # encoder #3 1,2,3
    # stompbuttons 1-3: 4,5,6
    # mode switch: 7, 8

    # stompbuttons from next three pins
    for i, pin in enumerate(st_but_pins):
        if mcp2.read_adc(pin) < 600:
            st_but_vals[i] = 0
        else:
            st_but_vals[i] = 1

    # mode switch from the last two pins
    _temp_mode = 2
    for i, pin in enumerate(mode_switch_pins):
        _val = mcp2.read_adc(pin)
        # print("mode switch {} : {}".format(i, _val))
        if _val < 700: # if the pin is low then the switch is in that position
            _temp_mode = i
    global mode_switch_val
    if mode_switch_val  != _temp_mode:
        mode_switch_val = _temp_mode
    return mode_switch_val

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

def powerButton():
    """
    this function checks the state of the power switch
    it it is low (in the off position) we shutdown the raspberrpy pi

    todo: needs to also indicate this with the neopixels
    """
    if pwr_but.readPwr():
        client.send_message(b"/shutdown", [1])

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

def setStompLED(color):
    strip.setPixelColor(1, color)
    strip.show()

def setStatusLED(color, b):
    strip.setPixelColor(0, color)
    strip.show()
    if b == 0:
        print("system bypass off stomp set to green")
        strip.setPixelColor(1, system.status_color)
        strip.show()
    else:
        print("system bypass on stomp set to red")
        strip.setPixelColor(1, Color(0,10,0))
        strip.show()

class SystemState():

    mode = "AM"
    gain = 1.0
    wet = 1.0
    pot_vals = [0,0,0]
    enc_vals = [0,0,0]
    bypass = 0
    status_color = Color(0,0,0)

    def _init__(self):
        print("created a new system state instance")

def boot(t=0.5):
    print("booting system")
    print("||||||||||||||||||||||||||||||||||||||")
    print("3")
    displayLines("Booting")
    setStatusLED(wheel(colors['RED']),1)
    strip.show()
    sleep(t)
    print("2")
    setStatusLED(wheel(colors['ORANGE']),1)
    strip.show()
    sleep(t)
    print("1")
    setStatusLED(wheel(colors['YELLOW']),1)
    strip.show()
    sleep(t)
    print("0")
    setStatusLED(wheel(colors['GREEN']),1)
    strip.show()

def mainLoop(system):
        enc = encoders.Encoders.getInstance(mcp1, mcp2)
        storeCurrentValues()
        readMCPs()
        e_change = enc.read()
        if e_change != -1:
            displayEncoderChange(e_change)
        sendOscOnChanges(system)
        powerButton()

if __name__ == "__main__":
    client = OSCClient('127.0.0.1', port=6449)
    osc = OSCThreadServer()
    sock = osc.listen(address='127.0.0.1', port=6450, default=True)
    osc.bind(b'/display', recvDisplayInfo)
    osc.bind(b'/pitch', recvPitchMsg)
    osc.bind(b'/switchInfo', recvSwitchInfo)
    osc.bind(b'/shutdown', recvShutdownMsg)
    osc.bind(b'/contEncoderInfo', recvContEncoderInfo)
    osc.bind(b'/disEncoderInfo', recvDisEncoderInfo)
    osc.bind(b'/modeInfo', recvModeInfo)
    osc.bind(b'/bypass', recvBypassInfo)
    system = SystemState()
    boot(0.1)
    while True:
        mainLoop(system)
