from flask import Flask
from flask import request
import threading
from werkzeug.serving import make_server

server = None
dataLock = threading.Lock()
stored_ip = None
thread = None
flask_app = Flask(__name__)

@flask_app.route("/")
def main():
    print("main")
    global stored_ip
    with dataLock:
        stored_ip = request.remote_addr
    return "Hello"

def get_stored_ip():
    with dataLock:
        return stored_ip


class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('0.0.0.0', 5000, app)
        self.ctx = flask_app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()

def start_server():
    global server
    server = ServerThread(flask_app)
    server.start()

def stop_server():
    global server
    server.shutdown()