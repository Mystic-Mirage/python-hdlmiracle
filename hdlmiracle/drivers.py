from hdlmiracle.datatypes import HexWord
from hdlmiracle.devices import Driver
from hdlmiracle.operationcodes import CHANNEL


__all__ = [
    'Dimmer',
]


class Dimmer(Driver):
    channels = {}

    def channel(self, channel, value=None):
        if value is None:
            return self.channels.setdefault(channel, 0)
        else:
            self.send(channel, value)

    def receive(self, packet):
        if packet.operation_code == CHANNEL:
            channel, value = packet.content[:2]
            self.channels[channel] = value

    def send(self, channel, value, delay=0):
        self.channels[channel] = value
        packet = self.packet(operation_code=CHANNEL,
                             content=(channel, value, HexWord(delay)))
        return packet
