# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


# Software SPI configuration:
# CLK  = 18
# MISO = 23
# MOSI = 24
# CS   = 25
# mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE0 = 0 # 0
SPI_DEVICE1 = 1 # 0

mcp1 = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE0))
mcp2 = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE1))

print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)
# Main program loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*16
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp1.read_adc(i)
    for i in range(8):
        values[i+8] = mcp2.read_adc(i)
    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} | {8:>4} | {9:>4} | {10:>4} | {11:>4} | {12:>4} | {13:>4} | {14:>4} | {15:>4} |'.format(*values))
    # Pause for a bit
    time.sleep(0.0125)
