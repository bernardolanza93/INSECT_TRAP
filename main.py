import cv2
import time
import urllib.request as urllib2
import sys
import os
"""
________________INFO_____________
Support for larger Lipo Battery of 5000 or 10,000 mAH+ to last up to 24 hrs +
Low power deep-sleep state with wake on interrupt/ calendar event
Low profile design to fit inside lots of existing Raspberry Pi cases!


"""




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


def capture_frame():

    cam_port = 0
    cam = cv2.VideoCapture(cam_port)


    result, image = cam.read()

    if result:

        # showing result, it take frame name and image
        # output


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

    capture_frame()

    if internet_on():
        print("sending image")
    else:
        print("no connection")



    print(temperature_of_raspberry_pi())
    sys.exit()

    time.sleep(3600)