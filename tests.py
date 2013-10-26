from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport

import unittest
from smartbus.packet import Packet


class TestPacket(unittest.TestCase):

    def setUp(self):
        self.raw_packet = bytes([
            0xc0, 0xa8, 0x4d, 0x66, 0x53, 0x4d, 0x41, 0x52, 0x54, 0x43, 0x4c,
            0x4f, 0x55, 0x44, 0xaa, 0xaa, 0x0f, 0xfe, 0x66, 0xff, 0xfe, 0x00,
            0x31, 0x01, 0xd5, 0x01, 0x2d, 0x00, 0x00, 0xe8, 0x4e
        ])
        self.packet = Packet(self.raw_packet)

    def test_crc(self):
        crc = self.raw_packet[-2] << 8 | self.raw_packet[-1]
        self.assertEqual(self.packet.crc, crc)

    def test_length(self):
        length = self.raw_packet[16]
        self.assertEqual(self.packet.length, length)

    def test_packed(self):
        self.assertEqual(self.packet.packed, self.raw_packet)
