from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *

from . import Device, OC_CHANNEL_CONTROL, sendmethod


ALL_CHANNELS = 255
CHANNEL_OFF = 0
CHANNEL_ON = 100


class DimmerRelay(Device):

    def __init__(self, netid, devid, channels=[]):
        super().__init__(netid=netid, devid=devid)
        self._channels = {k: v for k, v in enumerate(channels, start=1)}

    def receive_func(self, packet):
        if packet.opcode == OC_CHANNEL_CONTROL:
            self._channels[packet.data[0]] = packet.data[1]

    @sendmethod
    def _set_channel(self, channel, value):
        self._channels[channel] = value
        return self.packet(OC_CHANNEL_CONTROL, (channel, value, 0, 0))

    def channel(self, channel, value=None):
        if value is None:
            return self._channels.get(channel)
        else:
            self._set_channel(channel, value)
