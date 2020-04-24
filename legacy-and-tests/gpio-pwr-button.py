import RPi.GPIO as GPIO
from time import sleep

# GPIO Ports
but = 5


# initialize interrupt handlers
def init():
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)     # Use BCM mode
    # define the Encoder switch inputs
    GPIO.setup(but, GPIO.IN)
    # setup callback thread for the A and B encoder
    # use interrupts for all inputs
    # GPIO.add_event_detect(but, GPIO.RISING, callback=pwrInt)     # NO bouncetime
    return

# Rotarty encoder interrupt:
# this one is called for both inputs from rotary switch (A and B)
def pwrInt():
    # read both of the switches
    print("GPIO RISING")
    # now check if state of A or B has changed

# Main loop. Demonstrate reading, direction and speed of turning left/rignt
def main():
    init()          # Init interrupts, GPIO, ...
    while True :        # start test
        sleep(0.1)        # sleep 100 msec
        print(GPIO.input(but))

# start main demo function
main()


