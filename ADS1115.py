# sudo pip3 install Adafruit-ADS1x15
import time
from library import Adafruit_ADS1x15
import SQLfunction
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=0)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
# GAIN0 = 2/3
# GAIN1 = 2/3
# GAIN2 = 2/3
# GAIN3 = 2/3
GAIN = [8, 8, 8, 8]
# Start continuous ADC conversions on channel 0 using the previously set gain
# value.  Note you can also pass an optional data_rate parameter, see the simpletest.py
# example and read_adc function for more infromation.
# adc.start_adc(0, gain=GAIN0)
# Once continuous ADC conversions are started you can call get_last_result() to
# retrieve the latest result, or stop_adc() to stop conversions.

# Note you can also call start_adc_difference() to take continuous differential
# readings.  See the read_adc_difference() function in differential.py for more
# information and parameter description.
delay = 300
def analogportsread():
    # ch1 = adc.read_adc(0, gain=GAIN[0]) * (5.0 / 327670) #volts
    # ch1 = ch1 * 100 # temp
    # print(adc.read_adc(0, gain=GAIN[0]) * (5.0 / 327670) * 100)

    ports = 4
    value = [0, 0, 0, 0]

    for p in range(ports):
        try:
            val = adc.read_adc(p, gain=GAIN[p], data_rate=128) * (5.0 / 327670) * 100
        except Exception as E:
            val = 0
        else:
            value[p] = val
        print(val)

    SQLfunction.WriteToADS1115Table(value)
    # print(value) # Список из 4 int


if __name__ == '__main__':
    try:
        while True:
            analogportsread()
            time.sleep(delay)
    except KeyboardInterrupt:
        adc.stop_adc()
        print("Keyboard interrupt")



