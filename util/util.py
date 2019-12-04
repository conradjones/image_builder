import time
import os
from contextlib import contextmanager
import socket

def wait_for(condition, *, time_out=120, operation_name, wait_name):
    counter = 0;
    while not condition():
        if counter >= time_out:
            return False
        counter += 1
        time.sleep(1)

    return True


# Taken from https://github.com/conan-io/conan/blob/develop/conans/client/tools/files.py
# checkout conan it's a cool package manager for C/C++ :)
@contextmanager
def chdir(newdir):
    old_path = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(old_path)


class Cleanup:

    def __init__(self):
        self._cleanup_items = []

    def add(self, cleanup_fn):
        self._cleanup_items.append(cleanup_fn)

    def do_cleanup(self):
        for cleanup_item in reversed(self._cleanup_items):
            cleanup_item()


@contextmanager
def cleanup():
    cleanup_manager = Cleanup()
    try:
        yield cleanup_manager
    finally:
        cleanup_manager.do_cleanup()


def guess_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
