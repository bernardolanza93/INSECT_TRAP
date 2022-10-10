#!/usr/bin/python
import cv2
import time
import urllib.request as urllib2
import sys
import os
import multiprocessing

import subprocess
from subprocess import call
try:
    import RPi.GPIO as GPIO            # import RPi.GPIO module
except:
    print("lib not imported")

"""
________________INFO_____________
Support for larger Lipo Battery of 5000 or 10,000 mAH+ to last up to 24 hrs +
Low power deep-sleep state with wake on interrupt/ calendar event
Low profile design to fit inside lots of existing Raspberry Pi cases!


"""


AUTO_POWER_OFF = False
BUTTON_PIN = 10
LED_PINOUT = 1
BLINK_TIME = 10
PIN_2_ARDUINO = 5
AUTO_TERMINATION = True

def send_signal_2_arduino(PIN_2_ARDUINO):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
    GPIO.setup(PIN_2_ARDUINO, GPIO.OUT)  # set a port/pin as an output
    GPIO.output(PIN_2_ARDUINO, 1)  # set port/pin value to 1/GPIO.HIGH/True

    print("shutdown signal sended")
    time.sleep(15)



def temperature_of_raspberry_pi():
    try:
        cpu_temp = os.popen("vcgencmd measure_temp").readline()
        return cpu_temp.replace("temp=", "")
    except Exception as e:
        print("ERR: ",e)


def internet_on():
    try:
        urllib2.urlopen('http://python.org/', timeout=2)
        return True
    except urllib2.URLError as err:
        return False
def blink_led(button_state,blink_time,LED_PINOUT):
    print("blinking", blink_time)
    start = time.time()
    time_elapsed = 0
    while time_elapsed < BLINK_TIME and button_state.value == 0:  # Run forever
        GPIO.output(LED_PINOUT, GPIO.HIGH)  # Turn on
        time.sleep(0.5)  # Sleep for 1 second
        GPIO.output(LED_PINOUT, GPIO.LOW)  # Turn off
        time.sleep(0.5)  # Sleep for 1 second


def check_button_pressure(button_state,BLINK_TIME):
    GPIO.setwarnings(False)  # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
    GPIO.setup(BUTTON_PIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    # Set pin 10 to be an input pin and set initial value to be pulled low (off)
    start = time.time()
    time_elapsed = 0
    while time_elapsed < BLINK_TIME and button_state.value == 0:  # Run forever
        time.sleep(0.1)
        stop = time.time()
        time_elapsed = stop-start
        buttonState = GPIO.input(BUTTON_PIN)
        if buttonState == False:
            button_state.value = 1
            print("Button was pushed!")

        else:
            pass





def capture_frame():

    cam_port = 0
    cam = cv2.VideoCapture(cam_port)


    result, image = cam.read()

    if result:

        # saving image in local storage
        stamp = time.strftime("%m-%d-%Y_%H:%M:%S")

        cv2.imwrite("trap_" + stamp + ".jpg" , image)

        # If keyboard interrupt occurs, destroy image
        # window
        cv2.imshow("GeeksForGeeks", image)

        cv2.waitKey(1000)
        cv2.destroyWindow("GeeksForGeeks")

    else:
        print("No image detected. Please! try again")



while True:



    try:
        print(temperature_of_raspberry_pi())
    except:
        print("cannot read arduino temp")
    #sys.exit()


    time.sleep(5)
    button_state = multiprocessing.Value("i", 0)
    try:
        p1 = multiprocessing.Process(target=check_button_pressure(), args=(button_state,BLINK_TIME))
        p2 = multiprocessing.Process(target=blink_led(), args=(button_state, BLINK_TIME, LED_PINOUT))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        print("p1 is alive? -> {}".format(p1.is_alive()))
        print("p2 is alive? -> {}".format(p2.is_alive()))
    except:
        print("RPI button and led processes not running")

    if button_state.value == 1:
        if internet_on():
            print("internet ok, sending")
        else:
            print("no internet connection")
    else:
        print("normal running capturing...")

    capture_frame()

    time.sleep(2)


    try:
        send_signal_2_arduino(PIN_2_ARDUINO) #da qui dovrebbe spegnersi
    except:
        print("cannot send input to arduino for power off")

    if AUTO_TERMINATION == True:
        sys.exit()

    if AUTO_POWER_OFF:
        #controlla quale funziona
        subprocess.Popen(['shutdown', '-h', 'now'])
        call("sudo shutdown -h now", shell=True)
        #oppure switcha alla low power finche non viene spento da relay


