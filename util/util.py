import time


def wait_for(condition, operation_name, wait_name):
    counter = 0;
    timeout = 120
    while not condition():
        if counter >= timeout:
            return False
        counter += 1
        time.sleep(1)

    return True