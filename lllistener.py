from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *

from os import linesep
from time import sleep

import RPi.GPIO as GPIO

from smartbus import bus


def direction_setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.OUT)


def direction(direction):
    GPIO.output(12, direction)


def direction_in(*args):
    direction(GPIO.LOW)


def direction_out(*args):
    direction(GPIO.HIGH)


class Listener(bus.Device):

    def __init__(self):
        super().__init__()
        self.lines = 24

    def receive_func(self, packet):
        datarepr = []
        packet_len = len(packet.data)
        packet_lines = divmod(packet_len, 8)
        if packet_len:
            lines_p = packet_lines[0] + (1 if packet_lines[1] else 0)
        else:
            lines_p = 1
        self.lines += lines_p

        if self.lines > 23:
            print(
                'netid devid devtype opcode dstnet dstdev'
                '           hex              ascii'
            )
            self.lines = lines_p + 1

        for d in range(0, packet_len, 8):
            hexdata = []
            asciidata = []

            for i in packet.data[d:d + 8]:
                hexdata.append(format(i, '02x'))
                asciidata.append(chr(i) if i >= 0x20 and i < 0x7f else '.')

            datarepr.append(' '.join(hexdata).ljust(25) + ''.join(asciidata))

        datarepr_t = (linesep + ' ' * 42).join(datarepr)

        print(
            ' {0.src_netid:-3d}  '
            ' {0.src_devid:-3d}  '
            ' {0.src_devtype:-5d}  '
            '{0.opcode_hex} '
            ' {0.netid:-3d}   '
            ' {0.devid:-3d}    '
            '{1}'.format(packet, datarepr_t)
        )


def main():
    direction_setup()
    bus.init('/dev/ttyAMA0', 1, direction_in, direction_out)
    listener = Listener()
    print('G4 Listener Started...')

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        raise

    bus.quit()
    print('G4 Listener Stopped...')


if __name__ == '__main__':
    main()
