#!/usr/bin/python
import cv2
import time
import urllib.request as urllib2
import sys
import os
import multiprocessing
import logging
import subprocess
from pypylon import pylon

from datetime import datetime
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
BUTTON_PIN = 5
LED_PINOUT = 3
BLINK_TIME = 10
PIN_2_ARDUINO = 7
AUTO_TERMINATION = True
DEBUG=False




def check_folder(relative_path):
    """
    check_folder : check  the existence and if not, create the path for the results folder

    :param relative_path:path to be checked


    :return nothing:
    """

    workingDir = os.getcwd()
    path = workingDir + relative_path

    # Check whether the specified path exists or not
    isExist = os.path.exists(path)

    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)

        print("The new directory is created!", path)
    else:
        print('directory ok:', path)







def generic_blink(blink_interval_seconds,blink_times,PIN_LED):
    GPIO.setwarnings(False)  # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
    GPIO.setup(PIN_LED, GPIO.OUT,initial=GPIO.LOW)  # Set pin 8 to be an output pin and set initial value to low (off)
    for i in range(blink_times):
        #loggingR.info("time ele:", i)
        GPIO.output(PIN_LED, GPIO.HIGH)  # Turn on
        time.sleep(blink_interval_seconds)  # Sleep for 1 second
        GPIO.output(PIN_LED, GPIO.LOW)  # Turn off
        time.sleep(blink_interval_seconds)  # Sleep for 1 second
        i += 1
    GPIO.output(PIN_LED, GPIO.LOW)  # Turn off


def send_signal_2_arduino(PIN_2_ARDUINO):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)  # choose BCM or BOARD
    GPIO.setup(PIN_2_ARDUINO, GPIO.OUT, initial=GPIO.LOW)  # set a port/pin as an output

    for i in range(3):
        GPIO.output(PIN_2_ARDUINO, GPIO.HIGH)  # set port/pin value to 1/GPIO.HIGH/True

        loggingR.info("shutdown signal sended try... %s",str(i))
        time.sleep(1)
        GPIO.output(PIN_2_ARDUINO, GPIO.LOW)  # set port/pin value to 1/GPIO.HIGH/True
        time.sleep(0.5)
    GPIO.output(PIN_2_ARDUINO, GPIO.HIGH)  # set port/pin value to 1/GPIO.HIGH/True


def temperature_of_raspberry_pi():
    try:
        cpu_temp = os.popen("vcgencmd measure_temp").readline()
        return cpu_temp.replace("temp=", "")
    except Exception as e:
        loggingR.info("ERR: ",e)


def internet_on():
    try:
        urllib2.urlopen('http://python.org/', timeout=2)
        return True
    except urllib2.URLError as err:
        return False
def blink_led(button_state,blink_time,LED_PINOUT):
    GPIO.setwarnings(False)  # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
    GPIO.setup(LED_PINOUT, GPIO.OUT, initial=GPIO.LOW)  # Set pin 8 to be an output pin and set initial value to low (off)
    loggingR.info("blinking istants: %s", str(blink_time))
    i = 0
    while i < BLINK_TIME and button_state.value == 0:  # Run forever
        GPIO.output(LED_PINOUT, GPIO.HIGH)  # Turn on
        time.sleep(0.5)  # Sleep for 1 second
        GPIO.output(LED_PINOUT, GPIO.LOW)  # Turn off
        time.sleep(0.5)  # Sleep for 1 second
        i +=1
    GPIO.output(LED_PINOUT, GPIO.LOW)  # Turn off


def check_button_pressure(button_state,BLINK_TIME):
    GPIO.setwarnings(False)  # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
    GPIO.setup(BUTTON_PIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    # Set pin 10 to be an input pin and set initial value to be pulled low (off)
    i = 0
    while i < BLINK_TIME and button_state.value == 0:  # Run forever
        time.sleep(0.01)
        buttonState = GPIO.input(BUTTON_PIN)

        if buttonState == False:
            button_state.value = 1
            loggingR.info("Button was pushed!")
            print("pushed!")

        else:
            pass
        i += 1






def capture_frame():

    #cam_port = 2
    #cam = cv2.VideoCapture(cam_port)

    # conecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

    # Grabing Continusely (video) with minimal delay
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    converter = pylon.ImageFormatConverter()

    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    print(camera.IsGrabbing())
    if camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Access the image data
            image = converter.Convert(grabResult)
            img = image.GetArray()
            #cv2.namedWindow('title', cv2.WINDOW_NORMAL)
            #cv2.imshow('title', img)


            stamp = time.strftime("%m-%d-%Y_%H:%M:%S")

            cv2.imwrite("data/trap_" + stamp + ".jpg", img)

            grabResult.Release()
            camera.StopGrabbing()

            #cv2.destroyAllWindows()
    else:
        loggingR.info("No image detected. Please! try again")

    # Releasing the resource

'''
        stamp = time.strftime("%m-%d-%Y_%H:%M:%S")
        filename = "data/trap_" + stamp + ".png"
        img.Save(pylon.ImageFileFormat_Png, filename)



    else:
        loggingR.info("No image detected. Please! try again")


    camera.Close()
'''



check_folder("/data")
try:
    loggingR = logging.getLogger('RPI')
    loggingR.setLevel(logging.INFO)
    fh = logging.FileHandler('./data/RPI.log')
    fh.setLevel(logging.DEBUG)
    loggingR.addHandler(fh)
except Exception as e:
    print("ERROR LOGGING: ", e)



loggingR.info("____!!!!!!!_____starting BOOSE time____!!!!!!!_____: %s",datetime.now())

while True:


    try:
        loggingR.info(temperature_of_raspberry_pi())
    except:
        loggingR.info("cannot read arduino temp")
    #sys.exit()


    time.sleep(1)
    button_state = multiprocessing.Value("i", 0)
    try:
        loggingR.info("processing button and blinking start")
        p1 = multiprocessing.Process(target=check_button_pressure, args=(button_state,BLINK_TIME))
        p2 = multiprocessing.Process(target=blink_led, args=(button_state, BLINK_TIME, LED_PINOUT))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        loggingR.info("button process is alive? -> {}".format(p1.is_alive()))
        loggingR.info("blink process is alive? -> {}".format(p2.is_alive()))
    except Exception as e:
        loggingR.info("ERR multi proc: ", e)

    if button_state.value == 1:
        if internet_on():
            loggingR.info("internet ok, reaching telegram...")
            generic_blink(1, 5, LED_PINOUT)
            try:

                os.system('python bot.py')
                loggingR.info("bot started succefully")

            except Exception as e:
                loggingR.info("ERR bot: ", e)

            try:

                send_signal_2_arduino(PIN_2_ARDUINO)  # da qui dovrebbe spegnersi
                #forzo spegnimento se non arriva da arduino, anche arduino dopo un npo non aspettera piu segnali
                subprocess.Popen(['shutdown', '-h', 'now'])
                call("sudo shutdown -h now", shell=True)
            except:
                loggingR.info("cannot send input to arduino for power off")

        else:
            loggingR.info("no internet connection")
            generic_blink(0.1, 15, LED_PINOUT)



    else:
        print("normal mode_only CAPTURE")
        loggingR.info("normal running capturing...")
    try:
        capture_frame()
    except Exception as e:
        loggingR.info("capture cmera error %s",str(e))
        print(e)


    time.sleep(1)


    try:
        send_signal_2_arduino(PIN_2_ARDUINO) #da qui dovrebbe spegnersi
        time.sleep(1)
        #subprocess.Popen(['shutdown', '-h', 'now'])
        #call("sudo shutdown -h now", shell=True)
    except:
        loggingR.info("cannot send input to arduino for power off")


    if AUTO_TERMINATION == True:
        loggingR.info("termino male")
        sys.exit()



