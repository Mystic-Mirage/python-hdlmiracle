from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport

from ipaddress import IPv4Address
import struct


class Packet(object):

    def __init__(
        self, data=[], src_netid=3, src_devid=254, src_devtype=65534,
        op_code=0x000e, dst_netid=255, dst_devid=255, source_ip='127.0.0.1',
        hdlmiracle=False
    ):
        if type(data) == list:
            self.src_netid = src_netid
            self.src_devid = src_devid
            self.src_devtype = src_devtype
            self.op_code = op_code
            self.dst_netid = dst_netid
            self.dst_devid = dst_devid
            self.data = data
            self.source_ip = IPv4Address(source_ip)
            self.big = False
            self.hdlmiracle = hdlmiracle
        else:
            self.packed = data

    @property
    def crc(self):
        src_devtype = bytearray(struct.pack(b'!H', self.src_devtype))
        op_code = bytearray(struct.pack(b'!H', self.op_code))
        data = (
            [self.length, self.src_netid, self.src_devid] + list(src_devtype) +
            list(op_code) + [self.dst_netid, self.dst_devid] + self.data
        )
        checksum = 0
        for i in data:
            checksum = checksum ^ (i << 8)
            for _ in range(8):
                if (checksum & 0x8000) > 0:
                    checksum = (checksum << 1) ^ 0x1021
                else:
                    checksum = checksum << 1
            checksum = checksum & 0xffff
        return checksum

    @property
    def length(self):
        return 0xff if self.big else len(self.data) + 11

    @property
    def op_code_hex(self):
        return format(self.op_code, '#06x')

    @op_code_hex.setter
    def op_code_hex(self, value):
        if type(value) is int:
            self.op_code = value
        else:
            self.op_code = int(value, 16)

    @property
    def packed(self):
        src_ip = bytearray(self.source_ip.packed)
        src_id = bytearray([self.src_netid, self.src_devid])
        src_devtype = bytearray(struct.pack(b'!H', self.src_devtype))
        op_code = bytearray(struct.pack(b'!H', self.op_code))
        dst_id = bytearray([self.dst_netid, self.dst_devid])
        if self.hdlmiracle:
            head0 = bytearray(b'HDLMIRACLE')
        else:
            head0 = bytearray(b'SMARTCLOUD')
        head = bytearray([0xaa, 0xaa, self.length])
        data = bytearray(self.data)
        if self.big:
            crc = bytearray()
            data = bytearray([len(self.data) + 2]) + data
        else:
            crc = bytearray(struct.pack(b'!H', self.crc))
        return (
            src_ip + head0 + head + src_id + src_devtype + op_code + dst_id +
            data + crc
        )

    @packed.setter
    def packed(self, raw_packet):
        packet = bytearray(raw_packet)
        self.source_ip = IPv4Address('.'.join(str(x) for x in packet[:4]))
        if packet[4:].startswith(b'SMARTCLOUD'):
            self.hdlmiracle = False
        elif packet[4:].startswith(b'HDLMIRACLE'):
            self.hdlmiracle = True
        else:
            raise Exception('Not SmartBus packet')
        self.big = True if packet[16] == 0xff else False
        if not self.big and len(packet) != packet[16] + 16:
            raise Exception('Wrong packet length (%s). Expected value is %s'
                            % (packet[16], len(packet)))
        else:
            if self.big:
                packet_body = packet[17:]
            else:
                packet_body = packet[17:-2]
            self.src_netid = packet_body[0]
            self.src_devid = packet_body[1]
            self.src_devtype = packet_body[2] << 8 | packet_body[3]
            self.op_code = packet_body[4] << 8 | packet_body[5]
            self.dst_netid = packet_body[6]
            self.dst_devid = packet_body[7]
            if self.big:
                big_len0 = packet_body[8] << 8 | packet_body[9]
                big_len = len(self.data) + 2
                self.data = list(bytearray(packet_body[10:]))
                if big_len0 != big_len:
                    raise Exception('Wrong packet length (%s). Expected %s'
                                    % (big_len0, big_len))
            else:
                self.data = list(packet_body[8:])
                if packet[-2] << 8 | packet[-1] != self.crc:
                    raise Exception('Wrong checksum')
