from abc import ABC
import serial
import time
import threading


# Abstract base class that defines the interface 
# for an Arduino message listener.
class ArduinoListener(ABC):
    # Called when a message is received from the Arduino.
    # This method should be overridden by concrete 
    # listener implementations.
    def on_message(self, msg : list[str]):
        pass


# It establishes the serial connection, waits for readiness 
# confirmation, sends messages with unique identifiers, and 
# listens for responses in a separate thread.
class Arduino:

    connection = None
    listeners = {}
    arduino_listener_alive = False
    ready = False
    # Lock for a thread-safe writing operation
    serial_lock = threading.Lock()

    # Adds a message listener for a given unique ID
    # If the ID already exists, appends the listener to the list
    def addMessageListener(unique_id : str, listener : ArduinoListener):
        if unique_id in Arduino.listeners:
            Arduino.listeners[unique_id].append(listener)
        else:
            Arduino.listeners[unique_id] = [listener]
    
    # Removes a specific listener associated with a unique ID
    # If no listeners remain for that ID, the entry is deleted
    def removeListener(listener : ArduinoListener, unique_id : str):
        if unique_id in Arduino.listeners and listener in Arduino.listeners[unique_id]:
            Arduino.listeners[unique_id].remove(listener)
            if not Arduino.listeners[unique_id]:
                del Arduino.listeners[unique_id]

    # Notifies all listeners registered to a specific unique ID
    # Then removes the listeners after notifying them
    def notifyListeners(data, unique_id):

        if unique_id in Arduino.listeners:
            for listener in Arduino.listeners[unique_id]:
                listener.on_message(data)

            del Arduino.listeners[unique_id]

    # Connects to the Arduino on the given COM port and waits until it is ready
    # Starts the listener thread once ready
    def connect(com):
        try:
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
            return True
        except:
            return False
            

    # Sends a message to the Arduino with a unique ID
    # If a message handler is provided, it registers 
    # the handler to be called on response
    def send(dato, message_handler: ArduinoListener=None):
        with Arduino.serial_lock:
            if not Arduino.connection:
                raise Exception("Arduino not connected")      

            
            unique_id = str(int(time.time() * 1000))  # Unique ID based on current time in milliseconds
            print(f"Sending: {unique_id};{dato};")
            Arduino.connection.write(f"{unique_id};{dato};\n".encode())

            if message_handler:
                Arduino.addMessageListener(unique_id, message_handler)

            return unique_id        

    # Reads a line from the Arduino connection
    # Returns the decoded string or None if empty
    def read():
        try:
            data = Arduino.connection.readline().decode().strip()
            if data:
                return data
            else:
                return None
        except Exception as e:
            print(f"Error reading from Arduino: {e}")

    # Starts a separate thread to listen for incoming 
    # messages from Arduino
    def start_listener_thread():
        Arduino.arduino_listener_alive = True
        listener_thread = threading.Thread(target=Arduino.arduino_message_listener)
        listener_thread.start()


    # Continuously listens for messages from Arduino in a separate thread
    # When a message is received, notifies the corresponding listeners
    def arduino_message_listener():
        while Arduino.arduino_listener_alive:
            response = Arduino.read()
            if response:
                response = response.split(";")
                unique_id = response[0]
                Arduino.notifyListeners(response, unique_id)
        
