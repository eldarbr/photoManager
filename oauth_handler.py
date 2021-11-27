import http.server
import socketserver
from time import time, strftime, gmtime
import os
from config import Configurator
from urllib.parse import urlparse, parse_qs


my_server = socketserver
serving = True
oauth_token, oauth_token_expires = 0, 0


def request_token(oauth_id):
    os.system('explorer.exe "https://oauth.yandex.ru/authorize?response_type=token&client_id={}"'.format(oauth_id))


def receive_token():
    global my_server
    handler_object = MyHttpRequestHandler

    my_server = socketserver.TCPServer(("", 300), handler_object)
    while serving:
        my_server.handle_request()


def parse_token(path):
    global oauth_token, oauth_token_expires
    if "?" in path and "token" in path:
        if "error" in path:
            print("error!")
            print(path)
        else:
            arguments = parse_qs(urlparse(path).query)
            oauth_token = arguments["access_token"][0]
            expires_in = int(arguments["expires_in"][0])
            oauth_token_expires = str(int(time()) + expires_in)


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


if __name__ == "__main__":
    config = Configurator()
    oauth_id, oauth_token, oauth_token_expires = config.oauth_read()
    reobtain = "/"
    if len(oauth_token_expires) and time() < int(oauth_token_expires):
        while reobtain not in ("n", "N", "", "y", "Y"):
            reobtain = input("The previous token is still valid. Confirm token re-obtaining? [y/N]: ")
    if reobtain in ("y", "Y", "/"):
        request_token(oauth_id)
        receive_token()
    else:
        serving = False
    while serving:
        continue
    print(f"Token: {oauth_token}\nExpires at: {strftime('%d.%m.%Y %H:%M:%S', gmtime(int(oauth_token_expires)))}")
