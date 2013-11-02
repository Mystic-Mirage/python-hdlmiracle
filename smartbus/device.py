from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *


devices = {
    112: ('SB-DN-HVAC', 'HVAC Module'),
    118: ('SB-4Z-UN', '4 Zone Dry Contact'),
    149: ('SB-DDP', 'Dynamic Display Panel'),
    278: ('SB-3BS', '3 Buttons'),
    281: ('SB-6BS', '6 Buttons'),
    282: ('SB-4BS', '4 Buttons'),
    309: ('SB-9in1T-CL', '9 in 1 sensor'),
    314: ('SB-5in1TL-CL', '5 in 1 sensor'),
    313: ('SB-6in1TL-CL', '6 in 1 sensor'),
    306: ('SB-IR-UN', 'IR Emitter'),
    434: ('SB-RLY4c20A-DN', 'Relay 4ch 20A'),
    428: ('SB-RLY8c16A-DN', 'Relay 8ch 16A'),
    602: ('SB-DIM2c6A-DN', 'Dimmer 2ch 6A'),
    601: ('SB-DIM4c3A-DN', 'Dimmer 4ch 3A'),
    600: ('SB-DIM6c2A-DN', 'Dimmer 6ch 2A'),
    902: ('SB-ZAudio2-DN', 'Zone Audio'),
    1108: ('SB-Logic2-DN', 'Logic Module'),
    1201: ('SB-RSIP-DN', 'RS232IP Module'),
    3049: ('SB-SEC250K-DN', 'Security Module'),
}


class Device(object):
    list = []

    def __init__(
        self, devtype=None, netid=None, devid=None, register=True
    ):
        self._devtype = devtype
        self.netid = netid
        self.devid = devid
        if register:
            self.register()

    @classmethod
    def append(cls, device):
        if device not in cls.list:
            cls.list.append(device)
        else:
            raise Exception('Device already registered')

    @classmethod
    def remove(cls, device):
        if device in cls.list:
            cls.list.remove(device)
        else:
            raise Exception('Device not registered')

    @property
    def devtype(self):
        return self._devtype

    @property
    def info(self):
        if self.devtype in devices:
            return devices[self.devtype]
        else:
            return ('Unknown', 'Unknown')

    def receive(self, packet):
        if (
            (self.netid is None or packet.dst_netid in (self.netid, 255)) and
            (self.devid is None or packet.dst_devid in (self.devid, 255))
        ):
            self.receive_func(packet)

    def receive_func(self, packet):
        pass

    def register(self):
        self.append(self)

    def unregister(self):
        self.remove(self)
