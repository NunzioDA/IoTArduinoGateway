import time
from arduino_interface import Arduino
from listeners import CommandResponse, InfoManager
from tools import SmartParkAPI


# print message, useful for checking if it was successful
def on_command(command):
    print("Command received", command)
    Arduino.send(command, CommandResponse())

# Initializing the mqtt communication
SmartParkAPI.init(on_command=on_command)
SmartParkAPI.connect_mqtt()

# Connecting to arduino
connected = Arduino.connect("COM5")
wait_count = 0

if connected:    

    last_command_timestamp = None
    info_manager = InfoManager()

    # Main thread loop
    # This loop sends a request to the Arduino to check the environment state
    # by making an info request. If the state has changed, it is sent
    # to the MQTT broker.
    while True:              
        
        # Updating the enviroment status
        if not info_manager.waiting_info or wait_count > 3:
            Arduino.send("info", info_manager)
            info_manager.waiting_info = True
            wait_count = 0
        else:
            wait_count += 1

        time.sleep(2) 
else:
    print("Could not connect to Arduino.")
    print("Serial port already in use or Arduino is not connected.")

