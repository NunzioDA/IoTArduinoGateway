
import os
from dotenv import load_dotenv
import requests

import paho.mqtt.client as paho
from paho import mqtt
# This class is used to communicate with the WebServer.
#
class SmartParkAPI:
    password = ""
    mqtt_server = ""
    mqtt_username = ""
    mqtt_port = 0
    mqtt_commands_topic = ""

    on_command = None

    client = None

    # Loading base url and password
    # from a .env file
    @staticmethod
    def init(
        on_command = None,
    ):
        load_dotenv()
        SmartParkAPI.mqtt_username = os.getenv("MQTTUSERNAME")
        SmartParkAPI.password = os.getenv("PASSWORD")
        SmartParkAPI.mqtt_server = os.getenv("MQTTSERVER")
        SmartParkAPI.mqtt_port = int(os.getenv("MQTTPORT"))
        SmartParkAPI.mqtt_commands_topic = os.getenv("MQTT_COMMANDS_TOPIC")
        SmartParkAPI.mqtt_status_topic = os.getenv("MQTT_STATUS_TOPIC")
        SmartParkAPI.on_command = on_command

    ########################################
    # MQTT CALLBACKS
    ########################################
    # setting callbacks for different events to see if it works, print the message etc.
    def on_connect(client, userdata, flags, rc, properties=None):
        print("CONNACK received with code %s." % rc)

    # with this callback you can see if your publish was successful
    def on_publish(client, userdata, mid, properties=None):
        print("mid: " + str(mid))

    # print which topic was subscribed to
    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    # used to send the command to the specified callback function
    def on_message(client, userdata, msg):
        SmartParkAPI.on_command(msg.payload.decode())
    ########################################


    # This method is used to open a mqtt connection
    # and creates and return the relative client
    def connect_mqtt() -> paho.Client:
            
        if (SmartParkAPI.on_command is not None):
            client = paho.Client(client_id="ArduinoGateway", userdata=None, protocol=paho.MQTTv5)
            client.on_connect = SmartParkAPI.on_connect

            # enable TLS for secure connection
            client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
            # set username and password
            client.username_pw_set(SmartParkAPI.mqtt_username, SmartParkAPI.password)
            # connect to HiveMQ Cloud
            client.connect(SmartParkAPI.mqtt_server, SmartParkAPI.mqtt_port)

            client.on_subscribe = SmartParkAPI.on_subscribe
            client.on_message = SmartParkAPI.on_message
            client.on_publish = SmartParkAPI.on_publish
            client.subscribe(SmartParkAPI.mqtt_commands_topic, qos=2)
            client.loop_start()
            SmartParkAPI.client = client
        else:
            raise ValueError("SmartPark is not initialized, or the mqtt callbacks have not been passed during the initialization.")

    # This method is used to publish
    # the arduino status using mqtt
    def publish_status(status):
        SmartParkAPI.client.publish(SmartParkAPI.mqtt_status_topic, payload=status, qos=1, retain=True)

    # This method is used to make a 
    # get request. It automatically uses
    # the specified password in the .env
    @staticmethod
    def get_request(url, params) -> requests.Response:
        params["password"] = SmartParkAPI.password
        print(params)
        return requests.get(url, params)