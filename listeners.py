from arduino_interface import ArduinoListener
from tools import SmartParkAPI

# This class describes the listener that
# manages the info request response
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
        SmartParkAPI.publish_status(info)

# This is the listener that manages the
# arduino response to a general command
class CommandResponse(ArduinoListener):
    def __init__(self):
        self.info = None

    def on_message(self, message):
        print(f"received: {message[1]}")
