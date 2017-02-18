import unittest

from hdlmiracle.exceptions import (
    HDLMiracleIPAddressException,
    HDLMiraclePacketException,
)
from hdlmiracle.packet import Head, IPAddress, IPPacket, Packet


class TestIPAddress(unittest.TestCase):
    str_ip = '10.11.12.13'
    bytes_ip = b'\x0a\x0b\x0c\x0d'

    def test_from_bytes(self):
        ip = IPAddress(self.bytes_ip)
        self.assertEqual(ip, IPAddress(self.str_ip))

    def test_repr(self):
        ip = IPAddress(self.str_ip)
        self.assertEqual(repr(ip), repr(self.str_ip))

    def test_str(self):
        ip = IPAddress(self.str_ip)
        self.assertEqual(str(ip), self.str_ip)

    def test_to_iterable(self):
        ip = IPAddress(self.str_ip)
        ba = bytearray()
        ba.extend(ip)
        self.assertEqual(ba, self.bytes_ip)

    def test_wrong_byte_length(self):
        with self.assertRaises(HDLMiracleIPAddressException):
            IPAddress(b'\x0a\x0b\x0c')
        with self.assertRaises(HDLMiracleIPAddressException):
            IPAddress(b'\x0a\x0b\x0c\x0d\x0e')

    def test_wrong_str_length(self):
        with self.assertRaises(HDLMiracleIPAddressException):
            IPAddress('1234')
        with self.assertRaises(HDLMiracleIPAddressException):
            IPAddress('10.11.12')
        with self.assertRaises(HDLMiracleIPAddressException):
            IPAddress('10.11.12.13.14')


class TestIPPacket(unittest.TestCase):
    ip_head = b'\x7f\x00\x00\x01HDLMIRACLE'
    packet_data = b'\xaa\xaa\x0b\x01\xfa\xff\xfe\x00\x0e\x01\xff\x0d\x3f'
    raw_data = ip_head + packet_data

    def test_dict(self):
        ip_packet1 = IPPacket()
        ip_packet2 = IPPacket(**ip_packet1.dict())
        self.assertEqual(ip_packet1, ip_packet2)

    def test_from_raw(self):
        ip_packet = IPPacket(self.raw_data)
        self.assertEqual(ip_packet.ipaddress, IPAddress('127.0.0.1'))
        self.assertEqual(ip_packet.head, Head('HDLMIRACLE'))

    def test_from_packet(self):
        packet = Packet(self.packet_data)
        ip_packet = IPPacket(packet)
        self.assertEqual(packet, ip_packet)

    def test_ip_packet(self):
        ip_packet1 = IPPacket()
        ip_packet2 = IPPacket(bytes(ip_packet1))
        self.assertEqual(ip_packet1, ip_packet2)


class TestPacket(unittest.TestCase):
    raw_data = b'\xaa\xaa\x0b\x01\xfa\xff\xfe\x00\x0e\x01\xff\x0d\x3f'

    def test_changed(self):
        packet = Packet(self.raw_data)
        packet.target_subnet_id = 0xff
        self.assertEqual(packet.checksum, 0x3df1)

    def test_from_raw(self):
        packet = Packet(self.raw_data)
        self.assertEqual(packet.subnet_id, 0x01)
        self.assertEqual(packet.device_id, 0xfa)
        self.assertEqual(packet.device_type, 0xfffe)
        self.assertEqual(packet.operation_code, 0x000e)
        self.assertEqual(packet.target_subnet_id, 0x01)
        self.assertEqual(packet.target_device_id, 0xff)

    def test_from_raw_to_raw(self):
        packet = Packet(self.raw_data)
        self.assertEqual(bytes(packet), self.raw_data)

    def test_packet(self):
        packet1 = Packet()
        packet2 = Packet(bytes(packet1))
        self.assertEqual(packet1, packet2)

    def test_packet_big(self):
        packet1 = Packet(big=True)
        packet2 = Packet(bytes(packet1))
        self.assertEqual(packet1, packet2)

    def test_wrong(self):
        with self.assertRaises(HDLMiraclePacketException):
            Packet(b'!wrong!')


if __name__ == '__main__':
    unittest.main()
