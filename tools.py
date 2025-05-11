
import os
from dotenv import load_dotenv
import requests

# This class is used to communicate with the WebServer.
#
class WebServer:
    command_queue_file = "get_command_queue.php"
    status_script_file = "update_status.php"
    password = ""
    base_url = ""

    # Loading base url and password
    # from a .env file
    @staticmethod
    def init():
        load_dotenv()
        WebServer.base_url = os.getenv("BACKEND")
        WebServer.base_url = WebServer.base_url.encode('utf-8').decode('unicode_escape')
        WebServer.password = os.getenv("PASSWORD")
  
        WebServer.command_queue_file = WebServer.base_url + WebServer.command_queue_file
        WebServer.status_script_file = WebServer.base_url + WebServer.status_script_file

    # Ths method is used to update the
    # enviroment status on the webserver
    @staticmethod
    def update_status(info) -> requests.Response:
        return WebServer.get_request(WebServer.status_script_file, {"info": info})

    # This method is used to get the command
    # queue from the web server
    @staticmethod
    def get_command_queue(timestamp) -> requests.Response:
        return WebServer.get_request(WebServer.command_queue_file, {"timestamp": timestamp or "2015-01-01 00:00:00"})


    # This method is used to make a 
    # get request. It automatically uses
    # the specified password in the .env
    @staticmethod
    def get_request(url, params) -> requests.Response:
        params["password"] = WebServer.password
        print(params)
        return requests.get(url, params)