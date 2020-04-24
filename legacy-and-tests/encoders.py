# from gpiozero import Button
import RPi.GPIO as GPIO
from time import sleep

# all the available GPIO pins on the PI ordered from
# top left in a counter clockwise manner
GPIO.setmode(GPIO.BOARD)
board_pins = [7,11,12,13,15,16,18,22,29,31,32,33,35,36,37,38,40]
bcm_pins = [4,17,27,22,5,6,13,19,26,20,16,12,25,24,23,18]

buttons = []

def buttonPressed():
    print("button pressed")

# buttons.append(Button(17))
# buttons[0].when_pressed = buttonPressed

# for i, pin in enumerate(board_pins):
GPIO.setup(board_pins, GPIO.IN)
GPIO.add_event_detect(13, GPIO.RISING, callback=rotary_interrupt)
GPIO.add_event_detect(15, GPIO.RISING, callback=rotary_interrupt)

"""
for i, pin in enumerate(gpio_pins):
    buttons.append(Button(pin))
    buttons[i].when_pressed = buttonPressed
"""

clk_vals = [0,0]
dt_vals = [0,0]
dt_rising = False
clk_rising = False
event_detected = False


if __name__ == "__main__":
    while True:
        clk_vals[1] = clk_vals[0]
        clk_vals[0] = GPIO.input(15)
        dt_vals[1] = dt_vals[0]
        dt_vals[0] = GPIO.input(13)
        if dt_vals[0] > 0 and dt_vals[1] == 0:
            dt_rising = True
            # print("DT rising edge")
        if dt_vals[0] == 0 and dt_vals[1] > 0:
            dt_rising = False
            # print("DT falling edge")
        if clk_vals[0] > 0 and clk_vals[1] == 0:
            clk_rising = True
            # print("CLK rising edge")
        if clk_vals[0] == 0 and clk_vals[1] > 0:
            clk_falling = True
            # print("CLK falling edge")

        if dt_rising and clk_rising == 0 and event_detected == False:
            event_detected = True
            print("MOVING LEFT")
        if clk_rising and dt_rising == 0 and event_detected == False:
            event_detected = True
            print("MOVING RIGHT")
        if clk_vals[0] == 0 and dt_vals[0] == 0 and event_detected == True:
            event_detected = False
            print("Inbetween state")


        sleep(0.001)
