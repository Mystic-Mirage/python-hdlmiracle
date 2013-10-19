from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport

from os import linesep

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from smartbus.packet import Packet


class SmartListener(DatagramProtocol):

    def startProtocol(self):
        print('net_id  dev_id  dev_type  op_code  dst_net  dst_dev  data')
        self.transport.joinGroup('224.0.0.1')

    def datagramReceived(self, data, host_port):
        packet = Packet(data)
        datarepr = []
        for d in range(0, len(packet.data), 8):
            hexdata = []
            asciidata = []
            for i in packet.data[d:d + 8]:
                hexdata.append(format(i, '02x'))
                asciidata.append(chr(i) if i >= 0x20 and i < 0x7f else '.')
            datarepr.append(' '.join(hexdata).ljust(25) + ''.join(asciidata))
        datarepr_t = (linesep + ' ' * 53).join(datarepr)
        print(
            '{0.src_netid:-3d}     '
            '{0.src_devid:-3d}     '
            '{0.src_devtype:-5d}     '
            '{0.op_code_hex}   '
            '{0.dst_netid:-3d}      '
            '{0.dst_devid:-3d}      '
            '{1}'.format(packet, datarepr_t)
        )


if __name__ == '__main__':

    reactor.listenMulticast(6000, SmartListener())
    reactor.run()
