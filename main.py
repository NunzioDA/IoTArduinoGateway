import json
import time
from arduino_interface import Arduino
from listeners import CommandResponse, InfoManager
from tools import WebServer


# Initializing the webserver
WebServer.init()

# Connecting to arduino
Arduino.connect("COM5")
last_command_timestamp = None
info_manager = InfoManager()

# Main thread loop
# This loop will check for new commands in the queue
# sending them to arduino.
# It also update the enviroment status by making an info
# request to arduino and loading the result on the webserver.
while True:
    # Getting the command queue
    command_queue = WebServer.get_command_queue(
        timestamp=last_command_timestamp
    )
    print(command_queue.text)
    command_queue_json = json.loads(command_queue.text)

    # Checking for new commands in the queue
    for command in command_queue_json:
        # Check if the command is given later than the last command
        if last_command_timestamp is None or command["timestamp"] > last_command_timestamp:
            last_command_timestamp = command["timestamp"]
            command = command["command"]
            Arduino.send(command, CommandResponse())
    
    # Updating the enviroment status
    if not info_manager.waiting_info:
        Arduino.send("info", info_manager)
        info_manager.waiting_info = True


    time.sleep(2) 

