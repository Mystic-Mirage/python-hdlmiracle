from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *
from future.utils import with_metaclass

from ipaddress import IPv4Address
import struct


class _ClassProperty(object):

    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter

    def __get__(self, cls, owner):
        return getattr(cls, self.getter)()

    def __set__(self, cls, value):
        getattr(cls, self.setter)(value)


class _SourceIPMeta(type):

    source_ip = _ClassProperty('_get_source_ip', '_set_source_ip')


class Packet(with_metaclass(_SourceIPMeta, object)):

    src_netid = 3
    src_devid = 254
    src_devtype = 65534
    _source_ip = IPv4Address('127.0.0.1')

    @classmethod
    def _get_source_ip(cls):
        return cls._source_ip

    @classmethod
    def _set_source_ip(cls, ip):
        if type(ip) == IPv4Address:
            cls._source_ip = ip
        else:
            cls._source_ip = IPv4Address(ip)

    def __init__(
        self, data=bytearray(),
        op_code=0x000e, dst_netid=255, dst_devid=255,
        src_netid=None, src_devid=None, src_devtype=None,
        source_ip=None, hdlmiracle=False
    ):
        if type(data) == bytearray:
            self.data = data
            self.op_code = op_code
            self.dst_netid = dst_netid
            self.dst_devid = dst_devid
            if src_netid is not None:
                self.src_netid = src_netid
            if src_devid is not None:
                self.src_devid = src_devid
            if src_devtype is not None:
                self.src_devtype = src_devtype
            if source_ip is not None:
                self.source_ip = source_ip
            self.big = False
            self.hdlmiracle = hdlmiracle
        else:
            self.packed = data

    @property
    def crc(self):
        src_devtype = bytearray(struct.pack(b'!H', self.src_devtype))
        op_code = bytearray(struct.pack(b'!H', self.op_code))
        data = (
            bytearray([self.length, self.src_netid, self.src_devid]) +
            src_devtype +
            op_code +
            bytearray([self.dst_netid, self.dst_devid]) +
            self.data
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
        data = self.data
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
            raise Exception(
                'Wrong packet length ({0}). '
                'Expected value is {1}'.format(packet[16], len(packet))
            )
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
                self.data = packet_body[10:]
                if big_len0 != big_len:
                    raise Exception(
                        'Wrong packet length ({0}). '
                        'Expected {1}'.format(big_len0, big_len)
                    )
            else:
                self.data = packet_body[8:]
                if packet[-2] << 8 | packet[-1] != self.crc:
                    raise Exception('Wrong checksum')

    @property
    def source_ip(self):
        return self._source_ip

    @source_ip.setter
    def source_ip(self, ip):
        if type(ip) == IPv4Address:
            self._source_ip = ip
        else:
            self._source_ip = IPv4Address(ip)
