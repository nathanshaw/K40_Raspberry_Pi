import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

class PowerButton():
    def __init__(self):
        #set up the pwr_button
        # GPIO pin 5, pin# 29
        self.val = 0
        self.last_val = 0
        self.pin = 5

        self.gpio = GPIO
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setup(self.pin, self.gpio.IN)

    def readPwr(self):
        self.last_val = self.val
        self.val = (self.gpio.input(self.pin) - 1 ) * -1
        if self.val == 1 and self.last_val == 1:
            return 1
        return 0


