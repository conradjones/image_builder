import time
import os
from contextlib import contextmanager

def wait_for(condition, operation_name, wait_name):
    counter = 0;
    timeout = 120
    while not condition():
        if counter >= timeout:
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
