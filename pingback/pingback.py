from flask import Flask
from flask import request
import threading
from werkzeug.serving import make_server



class PingBack:

    def __init__(self):
        self.server = None
        self.dataLock = threading.Lock()
        self.stored_ip = None
        self.thread = None
        self.flask_app = Flask(__name__)
        self.flask_app.add_url_rule("/pingback/<ipaddress>", view_func=self.pingback)

    def pingback(self, ipaddress):
        with self.dataLock:
            self.stored_ip = ipaddress
        return "Hello"

    def get_stored_ip(self):
        with self.dataLock:
            return self.stored_ip


    class ServerThread(threading.Thread):

        def __init__(self, flask_app):
            threading.Thread.__init__(self)
            self.srv = make_server('0.0.0.0', 5000, flask_app)
            self.ctx = flask_app.app_context()
            self.ctx.push()

        def run(self):
            self.srv.serve_forever()

        def shutdown(self):
            self.srv.shutdown()

    def start_server(self):
        self.server
        self.server = PingBack.ServerThread(self.flask_app)
        self.server.start()

    def stop_server(self):
        self. server
        self.server.shutdown()