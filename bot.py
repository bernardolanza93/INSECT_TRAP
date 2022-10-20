#!/usr/bin/python
import telepot
import time
import os

import subprocess
import bot
from subprocess import call

path_here = os.getcwd()
path = path_here + "/data/"

def handleMessage(msg):
    id = msg['chat']['id'];
    command = msg['text'];
    print('Command ' + command + ' from chat id' + str(id));
    bot.sendMessage(id, "get data with this bot using /get_data , or terminate the appplication with /power_off")
    if (command == '/get_data'):

        # Initialize the camera

        # Seding picture
        for filename in os.listdir(path):
            #print(filename,os.listdir(path))
            if filename.endswith('.jpg'): #filetype >= 1.0.7
                bot.sendDocument(id, open(path + filename, 'rb'))
            elif filename.endswith('.log'):
                bot.sendDocument(id,open(path + filename, 'rb'))
            else:
                pass
    elif (command == '/power_off'):

        subprocess.Popen(['shutdown', '-h', 'now'])
        call("sudo shutdown -h now", shell=True)
    else:
        bot.sendMessage(id, "Command not found..")




bot = telepot.Bot('5648317998:AAHVraqqRq7NM1jXc4swH9SqDiiMUr2OegY');
bot.message_loop(handleMessage);
print("Listening to bot messages….");
while 1:
    time.sleep(10);

