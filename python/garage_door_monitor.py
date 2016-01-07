#!/usr/bin/env python2

# dB columns:
#   fully_open
#   fully_closed
#   indoor_button_detected
#   web_button_detected -- how to check this?
#   alarm_on
#   datetime

import RPi.GPIO as GPIO
import time
import simple_logger

### Hardware:
###     Button press detector:
###         Discrete NMOS + 1kOhm resistor:
###             Gate   = 5V garage door button positive terminal
###             Source = GND
###             Drain  = Rpi input (button_detect_pin), 1kOhm series to Rpi pin (use Rpi internal pull-up to 3.3V)
###     Button forcer:
###         Relay + diode + NMOS + 100kOhm resistor:
###             NMOS:
###                 Gate   = Rpi output (button_force_pin), with 100kOhm pull-down to GND
###                 Source = GND
###                 Drain  = Coil negative terminal
###             Coil terminals = NMOS Drain, Rpi 5V supply 
###                 Diode in reverse polarity across coil terminals
###             Normally Open output terminals = GND, 5V garage door button positive terminal
###     Buzzer driver:
###         Discrete NMOS + 100kOhm resistor + Piezo buzzer
###             NMOS:
###                 Gate   = Rpi output (alarm_pin), with 100kOhm pull-down to GND
###                 Source = GND
###                 Drain = Piezo negative terminal
###             Piezo buzzer terminals = Rpi 5V supply (or raw wall wart output?), NMOS drain
###     Should the buzzer be driven by a MOSFET?  Or direct from an output?


# Pin Definitons #### TODO: Change these!
alarm_pin = 2 
button_force_pin = 3 # Broadcom pin XX (Px pin XX) -- used to actuate relay to activate garage door opener
button_detect_pin = 17 # Broadcom pin 17 (P1 pin 11)
open_detect_pin = 27
closed_detect_pin = 22

GPIO.setmode(GPIO.BCM) # use broadcom numbering
### TODO: Change this to a pull-down
###         Or just change to a 
###         Need to verify that pin does not glitch high during power-up
GPIO.setup(button_detect_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button pin set as input w/ pull-up
GPIO.setup(open_detect_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(closed_detect_pin, GPIO.IN,pull_up_down=GPIO.PUD_UP)
#
GPIO.setup(alarm_pin,GPIO.OUT)
GPIO.setup(button_force_pin,GPIO.OUT)

alarm_on = False
### TODO: What format to use for these times?
alarm_start_time = 22.00 * 3600.0
alarm_stop_time  = 5.00 * 3600.0
force_close_time = 23.00 * 3600.0 ## the time at which the garage door opener will be actuated if the door is open

logger = simple_logger.logger("garagedoor")

def read_state():
    state = {}
    state["fully_open"] = GPIO.input(open_detect_pin)
    state["fully_closed"] = GPIO.input(closed_detect_pin)
    state["indoor_button_detected"] = GPIO.input(button_detect_pin)
    state["web_button_detected"] = False #### -- TODO: how to check this?
    state["alarm_on"] = alarm_on
    state["local_time"] = time.localtime()
    return state

def get_local_time(): 
    #### returns the current time of day, in seconds since midnight
    time_structure=time.localtime()
    return (time_structure.tm_hour*3600.0) + (time_structure.tm_min*60.0) + (time_structure.tm_sec)

current_state = read_state()
logger.store(current_state) ### Create a first state record
while True:
    last_state = current_state
    time.sleep(0.1) ## 100ms logging interval
    #### check alarms
    time_now = get_local_time()
    if ((time_now > alarm_start_time) or (time_now < alarm_stop_time))\
            and (not current_state["fully_closed"]):
        GPIO.output(alarm_pin,1)
        alarm_on = True
    else:
        GPIO.output(alarm_pin,0)
        alarm_on = False
    if (get_local_time() >= force_close_time) and (last_state["local_time"] < force_close_time)\
            and (not current_state["fully_closed"]):
        GPIO.output(button_force_pin,1)
        time.sleep(0.1)
        current_state = read_state()
        logger.store(current_state)
        last_state = current_state
        time.sleep(0.1) ### TODO: is 200ms long enough?
        GPIO.output(button_force_pin,0)
        time.sleep(0.1)
    current_state = read_state()
    if current_state != last_state:
        logger.store(current_state)
