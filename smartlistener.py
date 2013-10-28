from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport

from os import linesep
from time import sleep

import smartbus


class Listener(smartbus.device.Device):

    def __init__(self):
        super().__init__(self)
        self.lines = 24

    def receive(self, packet):
        datarepr = []

        packet_len = len(packet.data)
        packet_lines = divmod(packet_len, 8)
        lines_p = packet_lines[0] + 1 if packet_lines[1] > 0 else 0
        self.lines += lines_p

        if self.lines > 23:
            print(
                'netid devid devtype opcode dstnet dstdev'
                '           hex              ascii')
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
            '{0.op_code_hex} '
            ' {0.dst_netid:-3d}   '
            ' {0.dst_devid:-3d}    '
            '{1}'.format(packet, datarepr_t)
        )


if __name__ == '__main__':

    smartbus.init()
    listener = Listener()

    print('Smart-Bus Listener Started...')

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        raise

    print('Smart-Bus Listener Stopped...')

    smartbus.quit()
