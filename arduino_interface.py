from abc import ABC
import serial
import time
import threading

class ArduinoListener(ABC):
    def on_message(self, msg : list[str]):
        pass

class ArduinoReadyListener(ArduinoListener):
    def __init__(self, unique_id):
        self.unique_id = unique_id
        self.response_received = False
        self.response = None

    def on_message(self, msg):
        if self.unique_id in msg:
            self.response_received = True
            self.response = msg

class Arduino:

    connection = None
    listeners = {}
    arduino_listener_alive = False
    ready = False

    def addMessageListener(unique_id : str, listener : ArduinoListener):
        if unique_id in Arduino.listeners:
            Arduino.listeners[unique_id].append(listener)
        else:
            Arduino.listeners[unique_id] = [listener]
    
    def removeListener(listener : ArduinoListener, unique_id : str):
        if unique_id in Arduino.listeners and listener in Arduino.listeners[unique_id]:
            Arduino.listeners[unique_id].remove(listener)
            if not Arduino.listeners[unique_id]:
                del Arduino.listeners[unique_id]

    
    def notifyListeners(data, unique_id):

        if unique_id in Arduino.listeners:
            for listener in Arduino.listeners[unique_id]:
                listener.on_message(data)

            del Arduino.listeners[unique_id]
                
        

    def connect(com):
        Arduino.connection = serial.Serial(port=com, baudrate=9600, timeout=1)
        time.sleep(2)  # Wait for the connection to establish
        Arduino.send("ready;")

        while not Arduino.ready:        
            response = Arduino.read()

            if response :
                Arduino.ready = True
                print("Arduino is ready")
            else:
                Arduino.send("ready;")    

        if Arduino.ready:
            Arduino.start_listener_thread()

    def send(dato, message_handler: ArduinoListener=None):
        if not Arduino.connection:
            raise Exception("Arduino not connected")      

        
        unique_id = str(int(time.time() * 1000))  # Unique ID based on current time in milliseconds
        print(f"Sending: {unique_id};{dato};")
        Arduino.connection.write(f"{unique_id};{dato};\n".encode())

        if message_handler:
            Arduino.addMessageListener(unique_id, message_handler)

        return unique_id        


    def read():
        try:
            data = Arduino.connection.readline().decode().strip()
            if data:
                return data
            else:
                return None
        except Exception as e:
            print(f"Error reading from Arduino: {e}")

    def start_listener_thread():
        Arduino.arduino_listener_alive = True
        listener_thread = threading.Thread(target=Arduino.arduino_message_listener)
        listener_thread.start()

    def arduino_message_listener():
        while Arduino.arduino_listener_alive:
            response = Arduino.read()
            if response:
                response = response.split(";")
                unique_id = response[0]
                Arduino.notifyListeners(response, unique_id)
        
