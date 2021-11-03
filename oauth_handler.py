import http.server
import socketserver
from time import time
import os
from configparser import ConfigParser
from urllib.parse import urlparse, parse_qs


my_server = socketserver
serving = True


def read_config():
    config = ConfigParser()
    config.read("config.ini")
    id = config["Y.DISK"]["OAuthID"]
    return id


def request_token():
    oauth_id = read_config()
    os.system('explorer.exe "https://oauth.yandex.ru/authorize?response_type=token&client_id={}"'.format(oauth_id))
    receive_token()


def receive_token():
    global my_server
    handler_object = MyHttpRequestHandler

    my_server = socketserver.TCPServer(("", 300), handler_object)
    while serving:
        my_server.handle_request()


def write_config(token, expiration):
    config = ConfigParser()
    config.read("config.ini")
    config.set("Y.DISK", "OAuthToken", token)
    config.set("Y.DISK", "expires_at", expiration)
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def parse_token(path):
    if "?" in path and "token" in path:
        if "error" in path:
            print("error!")
            print(path)
        else:
            arguments = parse_qs(urlparse(path).query)
            token = arguments["access_token"][0]
            expires_in = int(arguments["expires_in"][0])
            expiration_time = str(int(time()) + expires_in)
            write_config(token, expiration_time)


def shutdown_server():
    global serving
    serving = False


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not ("?" in self.path):
            self.path = 'html pages/redirect.html'
            shutdown = False
        else:
            parse_token(self.path)
            self.path = 'html pages/success.html'
            shutdown = True
        self.headers="Cache-Control=no-cache"
        q = http.server.SimpleHTTPRequestHandler.do_GET(self)
        if shutdown:
            shutdown_server()
        return q
