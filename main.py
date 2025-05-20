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
    # This loop will check for new commands in the queue
    # sending them to arduino.
    # It also update the enviroment status by making an info
    # request to arduino and loading the result on the webserver.
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

