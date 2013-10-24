from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport

from os import linesep

import socket

from smartbus.packet import Packet


if __name__ == '__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(1)
    sock.bind(('', 6000))

    lines = 24

    print('Smart-Bus Listener Started...')

    while True:

        try:
            raw_packet = sock.recv(2048)
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            break

        packet = Packet(raw_packet)

        datarepr = []

        packet_len = len(packet.data)
        packet_lines = divmod(packet_len, 8)
        lines_p = packet_lines[0] + 1 if packet_lines[1] > 0 else 0
        lines += lines_p

        if lines > 23:
            print(
                'netid devid devtype opcode dstnet dstdev'
                '           hex              ascii')
            lines = lines_p + 1

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

    print('Smart-Bus Listener Stopped...')

    sock.close()
