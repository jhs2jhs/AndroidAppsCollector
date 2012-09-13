import time

def sleep_i(i):
    time.sleep(i)

def sleep():
    sleep_i(1)

def sleep_test():
    for i in range(1, 10):
        print i
        sleep()
