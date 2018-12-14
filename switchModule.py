# -*- coding: utf-8 -*-
"""
--------------------------------------------------------------------------
PocketBeagle Whack-a-Mole Game
--------------------------------------------------------------------------
License:   
Copyright 2017 Octavo Systems, LLC

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
Whack-a-Mole Game

  Please see README.txt for overview and how to run the game.
  
  Please sse run_whack_a_mole.sh for instructions to auto-run the game at 
boot


--------------------------------------------------------------------------
Software Setup:

  * Use the latest PocketBeagle image from BeagleBoard.org
  * Unzip the software package in a directory
  * Change the permissions on the run script:
      chmod 755 run_whack_a_mole.sh
  * Run the game:
      ./run_whack_a_mole.sh
  
  
--------------------------------------------------------------------------
Background Information: 
 
  * Using seven-segment digit LED display for Adafruit's HT16K33 I2C backpack:
    * http://adafruit.com/products/878
    * https://learn.adafruit.com/assets/36420
    * https://cdn-shop.adafruit.com/datasheets/ht16K33v110.pdf
    
    * Base code (adapted below):
        * https://github.com/emcconville/HT16K33/blob/master/FourDigit.py
        * https://github.com/emcconville/HT16K33/blob/master/_HT16K33.py
        * https://github.com/adafruit/Adafruit_Python_GPIO/blob/master/Adafruit_GPIO/Platform.py
        * https://github.com/adafruit/Adafruit_Python_GPIO/blob/master/Adafruit_GPIO/I2C.py
        * https://github.com/adafruit/Adafruit_Python_LED_Backpack/blob/master/Adafruit_LED_Backpack/HT16K33.py
        * https://github.com/adafruit/Adafruit_Python_LED_Backpack/blob/master/Adafruit_LED_Backpack/SevenSegment.py
        * https://github.com/adafruit/Adafruit_Python_LED_Backpack/blob/master/examples/sevensegment_test.py

"""
import time
import random

# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

# Peripheral path
GPIO_BASE_PATH               = "/sys/class/gpio"
ADC_BASE_PATH                = "/sys/bus/iio/devices/iio:device0"

# GPIO direction
IN                           = True
OUT                          = False

# GPIO output state
LOW                          = "0"
HIGH                         = "1"

# Start LEDs GPIO values
START_LED2                   = (3, 16)           # gpio112
START_LED1                   = (3, 17)           # gpio113
START_LED0                   = (3, 20)           # gpio116

# Button GPIO values
BUTTON0                      = (1, 12)           # gpio44 
BUTTON1                      = (2,  0)           # gpio64 
BUTTON2                      = (1, 20)           # gpio52 
BUTTON3                      = (1, 26)           # gpio58 

# LED GPIO values
LED0                         = (1, 14)           # gpio46 
LED1                         = (1, 15)           # gpio47 
LED2                         = (1, 28)           # gpio60 
LED3                         = (1, 27)           # gpio59 

# Potentiometer ADC input
POT                          = "in_voltage0_raw" # AIN0   
  
# Buzzer GPIO value
BUZZER                       = (1, 25)           # gpio57 

# Restart switch GPIO value
RESTART                      = (3, 19)           # gpio115

# HT16K33 values
DISPLAY_I2C_BUS              = 1                 # I2C 1  
DISPLAY_I2C_ADDR             = 0x70
DISPLAY_CMD                  = "i2cset -y 1 0x70"         


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

game_time                    = 30.0              # Game time (in seconds)

# Game action interval range
min_interval                 = 0.25              # Time (in seconds)
max_interval                 = 2.0               # Time (in seconds)

# ADC voltage range
min_adc_voltage              = 0
max_adc_voltage              = 1.65

# Range of (button, led) pairs on the board
min_actions                  = 0
max_actions                  = 3

# Number of points to display
score                        = 0

# Game array
game_array = [(BUTTON0, LED0), (BUTTON1, LED1), (BUTTON2, LED2), (BUTTON3, LED3)]


# ------------------------------------------------------------------------
# GPIO / ADC access library
# ------------------------------------------------------------------------
import os

def gpio_setup(gpio, direction, default_value=False):
    """Setup GPIO pin
    
      * Test if GPIO exists; if not create it
      * Set direction
      * Set default value
    """
    gpio_number = str((gpio[0] * 32) + gpio[1])
    path        = "{0}/gpio{1}".format(GPIO_BASE_PATH, gpio_number)
    
    if not os.path.exists(path):
        # "echo {gpio_number} > {GPIO_BASE_PATH}/export"
        print("Create GPIO: {0}".format(gpio_number))
        with open("{0}/export".format(GPIO_BASE_PATH), 'w') as f:
            f.write(gpio_number)
    
    if direction:
        # "echo in > {path}/direction"
        with open("{0}/direction".format(path), 'w') as f:
            f.write("in")
    else:
        # "echo out > {path}/direction"
        with open("{0}/direction".format(path), 'w') as f:
            f.write("out")
        
    if default_value:
        # "echo {default_value} > {path}/value"
        with open("{0}/value".format(path), 'w') as f:
            f.write(default_value)
    
# End def


def gpio_set(gpio, value):
    """Set GPIO ouptut value."""
    gpio_number = str((gpio[0] * 32) + gpio[1])
    path        = "{0}/gpio{1}".format(GPIO_BASE_PATH, gpio_number)
    
    # "echo {value} > {path}/value"
    with open("{0}/value".format(path), 'w') as f:
        f.write(value)

# End def


def gpio_get(gpio):
    """Get GPIO input value."""
    gpio_number = str((gpio[0] * 32) + gpio[1])
    path        = "{0}/gpio{1}".format(GPIO_BASE_PATH, gpio_number)
    
    # "cat {path}/value"
    with open("{0}/value".format(path), 'r') as f:
        out = f.read()
    
    return float(out)

# End def


def adc_get(channel):
    """Get ADC input value.
    
    Returns:
        value (float):  Value will be between 0 (0V) and 1.0 (1.8V)."""
    with open("{0}/{1}".format(ADC_BASE_PATH, channel), 'r') as f:
        out = f.read()
    
    return float(float(out) / float(4096))

# End def


# ------------------------------------------------------------------------
# Display Library
# ------------------------------------------------------------------------
HEX_DIGITS                  = [0x3f, 0x06, 0x5b, 0x4f,    # 0, 1, 2, 3
                               0x66, 0x6d, 0x7d, 0x07,    # 4, 5, 6, 7
                               0x7f, 0x6f, 0x77, 0x7c,    # 8, 9, A, b
                               0x39, 0x5e, 0x79, 0x71]    # C, d, E, F

CLEAR_DIGIT                 = 0x7F
POINT_VALUE                 = 0x80

DIGIT_ADDR                  = [0x00, 0x02, 0x06, 0x08]
COLON_ADDR                  = 0x04
                      
HT16K33_BLINK_CMD           = 0x80
HT16K33_BLINK_DISPLAYON     = 0x01
HT16K33_BLINK_OFF           = 0x00
HT16K33_BLINK_2HZ           = 0x02
HT16K33_BLINK_1HZ           = 0x04
HT16K33_BLINK_HALFHZ        = 0x06

HT16K33_SYSTEM_SETUP        = 0x20
HT16K33_OSCILLATOR          = 0x01

HT16K33_BRIGHTNESS_CMD      = 0xE0
HT16K33_BRIGHTNESS_HIGHEST  = 0x0F
HT16K33_BRIGHTNESS_DARKEST  = 0x00


def display_setup():
    """Setup display"""
    # i2cset -y 0 0x70 0x21
    os.system("{0} {1}".format(DISPLAY_CMD, (HT16K33_SYSTEM_SETUP | HT16K33_OSCILLATOR)))
    # i2cset -y 0 0x70 0x81
    os.system("{0} {1}".format(DISPLAY_CMD, (HT16K33_BLINK_CMD | HT16K33_BLINK_OFF | HT16K33_BLINK_DISPLAYON)))
    # i2cset -y 0 0x70 0xEF
    os.system("{0} {1}".format(DISPLAY_CMD, (HT16K33_BRIGHTNESS_CMD | HT16K33_BRIGHTNESS_HIGHEST)))

# End def

def display_clear():
    """Clear the display to read '0000'"""
    # i2cset -y 0 0x70 0x00 0x3F
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[0], HEX_DIGITS[0]))
    # i2cset -y 0 0x70 0x02 0x3F
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[1], HEX_DIGITS[0]))
    # i2cset -y 0 0x70 0x06 0x3F
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[2], HEX_DIGITS[0]))
    # i2cset -y 0 0x70 0x08 0x3F
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[3], HEX_DIGITS[0]))
    
    os.system("{0} {1} {2}".format(DISPLAY_CMD, COLON_ADDR, 0x0))
    
# End def


def display_set(data):
    """Display the data."""

    for i in range(0,3):
        display_set_digit(i, data[i])
    
# End def


def display_set_digit(digit_number, data, double_point=False):
    """Update the given digit of the display."""
    os.system("{0} {1} {2}".format(DISPLAY_CMD, DIGIT_ADDR[digit_number], display_encode(data, double_point)))    

# End def


def display_encode(data, double_point=False):
    """Encode data to TM1637 format."""
    ret_val = 0
    
    if (data != CLEAR_DIGIT):
        if double_point:
            ret_val = HEX_DIGITS[data] + POINT_VALUE
        else:
            ret_val = HEX_DIGITS[data]

    return ret_val

# End def



# ------------------------------------------------------------------------
# Demo Game Functions
# ------------------------------------------------------------------------

def get_time_interval():
    """Get the time interval to set the difficulty of the game.
    
    The time interval of button press is set by the potentiometer.  The max 
    voltage on the potentiometer is 1.65V and the minimum voltage is 0V.  The 
    value of 1.65V will set the maximum interval and a value of 0V will set 
    the minimum interval.  The time interval is determined by:
    
      interval_range = max_interval - min_interval
      interval_time  = min_interval + interval_range * (value / 1.65)

    Returns:
        interval_time (float): Time interval of game actions
    """
    interval_range = max_interval - min_interval
    adc_range      = max_adc_voltage - min_adc_voltage

    value = adc_get(POT) * 1.8                   # ADC range is 1.8V
    
    return min_interval + interval_range * (value / adc_range)
    
# End def


def update_display(value):
    """Update the value on the display."""
    
    # print("Score = {0}".format(value))    
    
    if (value == 0):
        display_clear()
    else:
        if (value < 10):
            display_set_digit(3, value)
        else:
            if (value < 100):
                display_set_digit(3, (value % 10))
                display_set_digit(2, (value / 10))
            else:
                if (value < 1000):
                    display_set_digit(3, (value % 10))
                    display_set_digit(2, ((value / 10) % 10))
                    display_set_digit(1, (value / 100))
                else:
                    if (value < 10000):
                        display_set_digit(3, (value % 10))
                        display_set_digit(2, ((value / 10) % 10))
                        display_set_digit(1, ((value / 100) % 10))
                        display_set_digit(0, (value / 1000))
                    else:
                        print ("Value too big to display.")
        
# End def


def update_score(clear=False):
    """Update the score
    """
    global score
    
    if (clear):
        score = 0
    else:
        score = score + 1
    
    update_display(score)
    
# End def


def game_action(number, interval):
    """Game action
    
    The game action will perform the following steps:
      * Light up the LED corresponding to the number
      * Poll the BUTTON corresponding to the number for interval seconds
      * If the button is pressed before interval seconds, then update the score
    """
    button = game_array[number][0]
    led    = game_array[number][1]

    gpio_set(led, HIGH)
    
    action_start = time.time()
    
    while ((time.time() - action_start) < interval):
        if not gpio_get(button):
            update_score()
            break
    
    gpio_set(led, LOW)    
    
# End def


def sound_buzzer(sleep_time):
    """Turn on the buzzer for time seconds."""
    gpio_set(BUZZER, HIGH)
    time.sleep(sleep_time)
    gpio_set(BUZZER, LOW)
    
# End def


def start_countdown_timer():
    """Start the countdown timer"""
    
    # Count 3
    # print("3")
    sound_buzzer(0.1)
    time.sleep(0.9)
    
    # Count 2
    # print("2")
    sound_buzzer(0.1)
    gpio_set(START_LED2, HIGH)
    time.sleep(0.9)

    # Count 1
    # print("1")
    sound_buzzer(0.1)
    gpio_set(START_LED1, HIGH)
    time.sleep(0.9)
    
    # Count 0
    # print("Start")
    gpio_set(START_LED0, HIGH)
    sound_buzzer(0.3)
    
    clear_countdown_timer_leds()
    
# End def    


def clear_countdown_timer_leds():
    """Clear countdown timer"""
    gpio_set(START_LED2, LOW)
    gpio_set(START_LED1, LOW)
    gpio_set(START_LED0, LOW)
    
# End def


def set_countdown_timer_leds():
    """Clear countdown timer"""
    gpio_set(START_LED2, HIGH)
    gpio_set(START_LED1, HIGH)
    gpio_set(START_LED0, HIGH)
    
# End def


def start_game():
    """Start the game.  The procedure is:
    
      * Set the interval based on the potentiometer
      * Start countdown timer
      * Set the start_time
      * While the curr_time - start_time is less than the game_time:
        * Pick a random number in [0, 1, 2, 3]
        * Perform a game action
      * Sound buzzer when time is up
    """
    interval   = get_time_interval()
    # print("interval = {0}".format(interval))
    
    start_countdown_timer()
    
    start_time = time.time()

    prev_action_number = None
    
    while ((time.time() - start_time) < game_time):
        action_number = random.randint(min_actions, max_actions)
        
        if (prev_action_number != action_number):
            game_action(action_number, interval)
            prev_action_number = action_number

    set_countdown_timer_leds()
    
    sound_buzzer(0.5)

    print("Final Score = {0}".format(score))
    
# End def


def setup_game():
    """Setup all the pins for the game."""
    print("Setup Game.")
    
    gpio_setup(START_LED2, OUT, LOW)
    gpio_setup(START_LED1, OUT, LOW)
    gpio_setup(START_LED0, OUT, LOW)

    gpio_setup(BUTTON0, IN)    
    gpio_setup(BUTTON1, IN)    
    gpio_setup(BUTTON2, IN)    
    gpio_setup(BUTTON3, IN)    

    gpio_setup(LED0, OUT, LOW)
    gpio_setup(LED1, OUT, LOW)
    gpio_setup(LED2, OUT, LOW)
    gpio_setup(LED3, OUT, LOW)
    
    gpio_setup(BUZZER, OUT, LOW)
    
    gpio_setup(RESTART, IN)
    
    display_setup()

# End def


def play_game():
    """Play the game."""
    print("Play Game.")
    clear_score = True
    game_done   = True
    
    while (True):
        if gpio_get(RESTART):
            if not game_done:
                print("Starting Game.")
                clear_score = True
                start_game()
                game_done = True
        else:
            if clear_score:
                update_score(clear=True)
                clear_countdown_timer_leds()
                clear_score = False
                game_done   = False

# End def


def cleanup_game():
    """Clean up the game."""    
    print("Cleanup Game.")
    # TBD

# End def


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':
    setup_game()
    
    try:
        play_game()
    except KeyboardInterrupt:
        pass

    cleanup_game()
    print("Game Finished.")



