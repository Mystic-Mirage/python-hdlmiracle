from __future__ import absolute_import

from .._packet import BusPacket, START_CODE


class BusPacketFromStream(object):

    def __init__(self):
        self.length = None
        self.prev_byte = None
        self.raw_packet = bytearray()
        self.start = False

    def extend(self, b_array):
        self.raw_packet.extend(b_array)
        self.length -= len(b_array)
        if self.length > 0:
            return False
        else:
            return True

    def get(self):
        try:
            return BusPacket.from_raw(self.raw_packet)
        except:
            return None

    def send(self, char):
        byte = ord(char)
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
            bytearray([self.prev_byte, byte]) == START_CODE
        ):
            self.start = True
            self.raw_packet.extend(START_CODE)
        self.prev_byte = byte
        return False
