import multiprocessing

import select
import time

import lcm

from .test_message import test_message


counter = 0


def sender(chanel: str):
    global counter
    while True:
        message = test_message()
        message.utime = counter
        counter += 1
        message.speed = 0.1 * counter
        message.direction = 'forward'

        _lcm = lcm.LCM()
        _lcm.publish(chanel, message.encode())
        print(f"\nSent test_message on {chanel}")
        time.sleep(2)


def listener(channel, data):
    message = test_message.decode(data)
    print(f"\nReceived test_message on {channel}")
    print(f"    {message.utime}")
    print(f"    {message.speed}")
    print(f"    {message.direction}")


if __name__ == '__main__':
    sender_process = multiprocessing.Process(target=sender, args=("TEST_1",))
    sender_process.start()
    sender_process = multiprocessing.Process(target=sender, args=("TEST_2",))
    sender_process.start()
    sender_process = multiprocessing.Process(target=sender, args=("TEST_3",))
    sender_process.start()

    lcm_1 = lcm.LCM()
    lcm_1.subscribe("TEST_1", listener)
    lcm_2 = lcm.LCM()
    lcm_2.subscribe("TEST_2", listener)
    lcm_3 = lcm.LCM()
    lcm_3.subscribe("TEST_3", listener)
    lcms = [lcm_1, lcm_2, lcm_3]

    timeout = 2
    while True:
        for i, _lcm in enumerate(lcms):
            try:
                rfds, wfds, efds = select.select([_lcm.fileno()], [], [],
                                                 timeout)
                if rfds:
                    _lcm.handle()
                else:
                    print("\nLCM 1: Waiting...")
            except KeyboardInterrupt:
                break
