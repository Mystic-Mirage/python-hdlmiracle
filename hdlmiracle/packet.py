from binascii import crc_hqx
from collections import Iterable, OrderedDict

from .datatypes import (
    DeviceAddress,
    Head,
    HexArray,
    HexByte,
    HexWord,
    IPAddress,
)
from .exceptions import HDLMiraclePacketError
from .helpers import PY3, Property, ReprMixin
from .operationcodes import SEARCH


__all__ = [
    'ALL_DEVICES',
    'ALL_NETWORKS',
    'HDLMIRACLE',
    'HEADS',
    'IPPacket',
    'Packet',
    'SMARTCLOUD',
]


ALL_NETWORKS = 0xff
ALL_DEVICES = 0xff

DEFAULT_SUBNET_ID = 0xbb
DEFAULT_DEVICE_ID = 0xbb
DEFAULT_DEVICE_TYPE = 0xdddd
DEFAULT_IPADDRESS = '127.0.0.1'

CREEPYFROG = 'CREEPYFROG'
HDLMIRACLE = 'HDLMIRACLE'
SMARTCLOUD = 'SMARTCLOUD'

HEADS = [HDLMIRACLE, SMARTCLOUD]

START_CODE = b'\xaa\xaa'


class Packet(ReprMixin):
    subnet_id = Property(HexByte(DEFAULT_SUBNET_ID))
    device_id = Property(HexByte(DEFAULT_DEVICE_ID))
    device_type = Property(HexWord(DEFAULT_DEVICE_TYPE))
    operation_code = Property(HexWord(SEARCH))
    target_subnet_id = Property(HexByte(ALL_NETWORKS))
    target_device_id = Property(HexByte(ALL_DEVICES))
    content = Property(HexArray())
    big = Property(False)

    def __new__(cls, source=None, address=None, subnet_id=None, device_id=None,
                device_type=None, operation_code=None, target_address=None,
                target_subnet_id=None, target_device_id=None, content=None,
                big=None, **kwargs):
        if source:
            if isinstance(source, Packet):
                return object.__new__(cls, **source.dict())
            if isinstance(source, Iterable):
                if PY3 and isinstance(source, str):
                    source = source.encode('latin-1')
                return cls._from_raw(source)
        self = object.__new__(cls)
        try:
            self.address = address
            self.subnet_id = subnet_id
            self.device_id = device_id
            self.device_type = device_type
            self.operation_code = operation_code
            self.target_address = target_address
            self.target_subnet_id = target_subnet_id
            self.target_device_id = target_device_id
            self.content = content
            self.big = big
        except ValueError:
            raise HDLMiraclePacketError('Error in packet data')
        return self

    @classmethod
    def _from_raw(cls, data):
        self = object.__new__(cls)
        packet = bytearray(data)
        packet_start = packet[:2]
        if packet_start != START_CODE:
            raise HDLMiraclePacketError('Not a SmartBus packet')
        self.big = packet[2] > 128
        self.subnet_id = packet[3]
        self.device_id = packet[4]
        self.device_type = packet[5:7]
        self.operation_code = packet[7:9]
        self.target_subnet_id = packet[9]
        self.target_device_id = packet[10]
        if self.big:
            packet_length = HexWord(packet[11:13])
            self.content = packet[13:packet_length+11]
        else:
            packet_length = packet[2]
            self.content = packet[11:packet_length]
            packet_checksum = HexWord(packet[packet_length:packet_length+2])
            checksum = self.checksum
            if packet_checksum != checksum:
                raise HDLMiraclePacketError(
                    'Wrong checksum ({0}). '
                    'Expected {1}'.format(packet_checksum, checksum)
                )
        length = self.length
        if packet_length != length:
            raise HDLMiraclePacketError(
                'Wrong packet length ({0}). '
                'Expected value is {1}'.format(packet_length, length)
            )
        return self

    @property
    def address(self):
        return DeviceAddress(self.subnet_id, self.device_id)

    @address.setter
    def address(self, device_address):
        if device_address is not None:
            self.subnet_id, self.device_id = device_address

    @property
    def checksum(self):
        data = HexArray([
            self.length,
            self.subnet_id,
            self.device_id,
            self.device_type,
            self.operation_code,
            self.target_subnet_id,
            self.target_device_id,
            self.content,
        ])
        return HexWord(crc_hqx(data, 0))

    def dict(self):
        _dict = OrderedDict()
        _dict['subnet_id'] = self.subnet_id
        _dict['device_id'] = self.device_id
        _dict['device_type'] = self.device_type
        _dict['operation_code'] = self.operation_code
        _dict['target_subnet_id'] = self.target_subnet_id
        _dict['target_device_id'] = self.target_device_id
        _dict['content'] = self.content
        if self.big:
            _dict['big'] = self.big
        return _dict

    @property
    def length(self):
        if self.big:
            return HexWord(len(self.content) + 2)
        return HexByte(len(self.content) + 11)

    @property
    def target_address(self):
        return DeviceAddress(self.target_subnet_id, self.target_device_id)

    @target_address.setter
    def target_address(self, device_address):
        if device_address is not None:
            self.target_subnet_id, self.target_device_id = device_address

    def __eq__(self, other):
        return all([
            self.subnet_id == other.subnet_id,
            self.device_id == other.device_id,
            self.device_type == other.device_type,
            self.operation_code == other.operation_code,
            self.target_subnet_id == other.target_subnet_id,
            self.target_device_id == other.target_device_id,
            self.content == other.content,
            self.big == other.big,
        ])

    def __iter__(self):
        data = HexArray([
            START_CODE,
            0xff if self.big else self.length,
            self.subnet_id,
            self.device_id,
            self.device_type,
            self.operation_code,
            self.target_subnet_id,
            self.target_device_id,
            self.length if self.big else None,
            self.content,
            None if self.big else self.checksum,
        ])
        return iter(data)

    def __str__(self):
        data = bytearray(self)
        return str(data, 'latin-1') if PY3 else str(data)


class IPPacket(Packet):
    ipaddress = Property(IPAddress(DEFAULT_IPADDRESS))
    head = Property(Head(HDLMIRACLE))

    def __new__(cls, source=None, ipaddress=None, head=None, address=None,
                subnet_id=None, device_id=None, device_type=None,
                operation_code=None, target_address=None,
                target_subnet_id=None, target_device_id=None, content=None,
                big=False, **kwargs):
        if source:
            if isinstance(source, Packet):
                return Packet.__new__(cls, **source.dict())
            if isinstance(source, Iterable):
                if PY3 and isinstance(source, str):
                    source = source.encode('latin-1')
                return cls._from_raw(source)
        self = Packet.__new__(
            cls,
            address=address,
            subnet_id=subnet_id,
            device_id=device_id,
            device_type=device_type,
            operation_code=operation_code,
            target_address=target_address,
            target_subnet_id=target_subnet_id,
            target_device_id=target_device_id,
            content=content,
            big=big,
        )
        try:
            self.ipaddress = ipaddress
            self.head = head
        except ValueError:
            raise HDLMiraclePacketError('Error in packet data')
        return self

    def dict(self):
        _dict = OrderedDict()
        _dict['ipaddress'] = self.ipaddress
        _dict['head'] = self.head
        _dict.update(Packet.dict(self))
        return _dict

    @classmethod
    def _from_raw(cls, data):
        data = bytearray(data)
        self = IPPacket(Packet._from_raw(data[14:]))
        self.ipaddress = IPAddress(data[:4])
        self.head = Head(data[4:14])
        return self

    def __iter__(self):
        data = HexArray([
            self.ipaddress,
            self.head,
            Packet.__iter__(self),
        ])
        return iter(data)
