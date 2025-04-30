import json
import time
from arduino_interface import Arduino, ArduinoListener
import requests

base_url = "https://www.coinquilinipercaso.altervista.org/IoTProject/"
command_queue_file = "get_command_queue.php"
status_script_file = "update_status.php"


last_command_timestamp = None

class InfoManager(ArduinoListener):
    def __init__(self):
        self.info = None
        self.waiting_info = False

    def on_message(self, message):
        self.on_info(message[1])
        self.waiting_info = False

    def on_info(self, info):
        # sending info to the server
        print(f"Info received: {info}")
        r = requests.get(base_url+status_script_file, {"info": info, "password": "_riNzDo27P29oco"})
        print(r.text)

class CommandResponse(ArduinoListener):
    def __init__(self):
        self.info = None

    def on_message(self, message):
        print(f"received: {message[1]}")

info_manager = InfoManager()

Arduino.connect("COM3")

while True:
    command_queue = requests.get(base_url+command_queue_file, {"password": "_riNzDo27P29oco", "timestamp": last_command_timestamp or "2015-01-01 00:00:00"})
    command_queue_json = json.loads(command_queue.text)

    for command in command_queue_json:
        # Check if the command is given later than the last command
        if last_command_timestamp is None or command["timestamp"] > last_command_timestamp:
            last_command_timestamp = command["timestamp"]
            command = command["command"]
            Arduino.send(command, CommandResponse())
    
    if not info_manager.waiting_info:
        Arduino.send("info", info_manager)
        info_manager.waiting_info = True


    time.sleep(2) 

