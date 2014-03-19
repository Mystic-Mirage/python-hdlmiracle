from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *
from future.utils import with_metaclass

from ipaddress import IPv4Address
import struct

from ._opcode import OC_SEARCH


ALL_NETWORKS = 255
ALL_DEVICES = 255

_bus_head = bytearray([0xaa, 0xaa])
_g3_head = bytearray(b'HDLMIRACLE')
_g4_head = bytearray(b'SMARTCLOUD')


def _crc(packet_array):
    checksum = 0
    for i in packet_array:
        checksum = checksum ^ (i << 8)
        for _ in range(8):
            if (checksum & 0x8000) > 0:
                checksum = (checksum << 1) ^ 0x1021
            else:
                checksum = checksum << 1
        checksum = checksum & 0xffff
    return checksum


def _join_bytearrays(*args):
    return bytearray.join(bytearray(), args)


class _ClassProperty(object):

    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter

    def __get__(self, cls, owner):
        return getattr(cls, self.getter)()

    def __set__(self, cls, value):
        getattr(cls, self.setter)(value)


class _SourceIPMeta(type):
    src_ipaddress = _ClassProperty('_get_src_ipaddress', '_set_src_ipaddress')


class BusFromStream(object):

    def __init__(self):
        self.length = None
        self.prev_byte = None
        self.raw_packet = None
        self.start = False

    def get(self):
        try:
            return BusPacket.from_raw(self.raw_packet)
        except:
            return None

    def send(self, byte):
        if self.start:
            if self.length is None:
                self.length = byte
            self.raw_packet.append(byte)
            self.length -= 1
            if self.length > 0:
                return False
            else:
                return True
        if (
            not self.start and
            self.prev_byte is not None and
            bytearray([self.prev_byte, byte]) == _bus_head
        ):
            self.start = True
            self.raw_packet = list(_bus_head)
        self.prev_byte = byte
        return False


class BusPacket(object):
    src_netid = 254
    src_devid = 254
    src_devtype = 65534

    def __new__(cls, opcode=OC_SEARCH, data=[], netid=ALL_NETWORKS,
        devid=ALL_DEVICES, src_netid=None, src_devid=None, src_devtype=None,
        big=False):

        self = object.__new__(cls)
        self.opcode = opcode
        self.data = list(data)
        self.netid = netid
        self.devid = devid
        if src_netid is not None:
            self.src_netid = src_netid
        if src_devid is not None:
            self.src_devid = src_devid
        if src_devtype is not None:
            self.src_devtype = src_devtype
        self.big = big
        return self

    @classmethod
    def from_raw(cls, raw_packet):
        self = object.__new__(cls)
        packet = bytearray(raw_packet)
        if not packet.startswith(_bus_head):
            raise Exception('Not SmartBus packet')
        self.big = True if packet[2] == 0xff else False
        packet_len = len(packet) - 2
        if not self.big and packet_len != packet[2]:
            raise Exception('Wrong packet length ({0}). '
                'Expected value is {1}'.format(packet[2], packet_len))
        else:
            if self.big:
                packet_body = packet[3:]
            else:
                packet_body = packet[3:-2]
            self.src_netid = packet_body[0]
            self.src_devid = packet_body[1]
            self.src_devtype = packet_body[2] << 8 | packet_body[3]
            self.opcode = packet_body[4] << 8 | packet_body[5]
            self.netid = packet_body[6]
            self.devid = packet_body[7]
            if self.big:
                big_len0 = packet_body[8] << 8 | packet_body[9]
                self.data = list(packet_body[10:])
                big_len = len(self.data) + 2
                if big_len0 != big_len:
                    raise Exception('Wrong packet length ({0}). '
                        'Expected {1}'.format(big_len0, big_len))
            else:
                self.data = list(packet_body[8:])
                if packet[-2] << 8 | packet[-1] != self.crc():
                    raise Exception('Wrong checksum')
        return self

    def crc(self):
        packet_array = _join_bytearrays(
            bytearray([self.length(), self.src_netid, self.src_devid]),
            bytearray(struct.pack(b'!H', self.src_devtype)),
            bytearray(struct.pack(b'!H', self.opcode)),
            bytearray([self.netid, self.devid]),
            bytearray(self.data)
        )
        return _crc(packet_array)

    def length(self):
        return 0xff if self.big else len(self.data) + 11

    @property
    def opcode_hex(self):
        return format(self.opcode, '#06x')

    @opcode_hex.setter
    def opcode_hex(self, value):
        if type(value) is int:
            self.opcode = value
        else:
            self.opcode = int(value, 16)

    @property
    def opcode_hex0(self):
        return format(self.opcode, '04x')

    def packed(self):
        src = bytearray([self.src_netid, self.src_devid])
        src_devtype = bytearray(struct.pack(b'!H', self.src_devtype))
        opcode = bytearray(struct.pack(b'!H', self.opcode))
        dst = bytearray([self.netid, self.devid])
        length = bytearray([self.length()])
        data = bytearray(self.data)
        if self.big:
            big_len = bytearray([len(self.data) + 2])
            packed = _join_bytearrays(_bus_head, length, src, src_devtype,
                opcode, dst, big_len, data)
        else:
            body = _join_bytearrays(length, src, src_devtype, opcode, dst,
                data)
            crc = bytearray(struct.pack(b'!H', _crc(body)))
            packed = _join_bytearrays(_bus_head, body, crc)
        return bytes(packed)


class Packet(with_metaclass(_SourceIPMeta, BusPacket)):
    _src_ipaddress = IPv4Address('127.0.0.1')
    hdl = False

    @classmethod
    def _get_src_ipaddress(cls):
        return cls._src_ipaddress

    @classmethod
    def _set_src_ipaddress(cls, ipaddress):
        if type(ipaddress) == IPv4Address:
            cls._src_ipaddress = ipaddress
        else:
            cls._src_ipaddress = IPv4Address(ipaddress)

    def __new__(cls, opcode=OC_SEARCH, data=[], netid=ALL_NETWORKS,
        devid=ALL_DEVICES, src_netid=None, src_devid=None, src_devtype=None,
        big=False, src_ipaddress=None, hdl=None):

        self = BusPacket.__new__(cls, opcode, data, netid, devid, src_netid,
            src_devid, src_devtype, big)
        if src_ipaddress is not None:
            self.src_ipaddress = src_ipaddress
        if hdl is not None:
            self.hdl = hdl
        return self

    @classmethod
    def from_bus(cls, bus_packet):
        self = BusPacket.__new__(cls, bus_packet.opcode, bus_packet.data,
            bus_packet.netid, bus_packet.devid, bus_packet.src_netid,
            bus_packet.src_devid, bus_packet.src_devtype, bus_packet.big)
        return self

    @classmethod
    def from_raw(cls, raw_packet):
        packet = bytearray(raw_packet)
        if packet[4:].startswith(_g3_head):
            hdl = True
        elif packet[4:].startswith(_g4_head):
            hdl = False
        else:
            raise Exception('Not SmartBus packet')
        self = BusPacket.from_raw(packet[14:])
        self.src_ipaddress = IPv4Address('.'.join(map(str, packet[:4])))
        self.hdl = hdl
        return self

    def packed(self):
        src_ipaddress = bytearray(self.src_ipaddress.packed)
        if self.hdl:
            head0 = _g3_head
        else:
            head0 = _g4_head
        bus_packet = bytearray(BusPacket.packed(self))
        packed = _join_bytearrays(src_ipaddress, head0, bus_packet)
        return bytes(packed)

    def to_bus(self):
        return BusPacket(self.opcode, self.data, self.netid, self.devid,
            self.src_netid, self.src_devid, self.src_devtype, self.big)

    @property
    def src_ipaddress(self):
        return self._src_ipaddress

    @src_ipaddress.setter
    def src_ipaddress(self, ipaddress):
        if type(ipaddress) == IPv4Address:
            self._src_ipaddress = ipaddress
        else:
            self._src_ipaddress = IPv4Address(ipaddress)
