from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *

from threading import Event


TYPES = {
    32: ('SB-DMX48-DN', 'DMX48'),
    112: ('SB-DN-HVAC', 'HVAC Module'),
    118: ('SB-4Z-UN', '4 Zone Dry Contact'),
    149: ('SB-DDP-EU', 'Dynamic Display Panel'),
    278: ('SB-3BS-EU', '3 Buttons'),
    281: ('SB-6BS-EU', '6 Buttons'),
    282: ('SB-4BS-EU', '4 Buttons'),
    306: ('SB-IR-UN', 'IR Emitter'),
    309: ('SB-9in1T-CL', '9 in 1 sensor'),
    313: ('SB-6in1TL-CL', '6 in 1 sensor'),
    314: ('SB-5in1TL-CL', '5 in 1 sensor'),
    428: ('SB-RLY8c16A-DN', 'Relay 8ch 16A'),
    434: ('SB-RLY4c20A-DN', 'Relay 4ch 20A'),
    600: ('SB-DIM6c2A-DN', 'Dimmer 6ch 2A'),
    601: ('SB-DIM4c3A-DN', 'Dimmer 4ch 3A'),
    602: ('SB-DIM2c6A-DN', 'Dimmer 2ch 6A'),
    898: ('SB-4LED-DCV', 'LED Dimmer 4ch'),
    902: ('SB-ZAudio2-DN', 'Zone Audio'),
    1108: ('SB-Logic2-DN', 'Logic Module'),
    1201: ('SB-RSIP-DN', 'RS232IP Module'),
    3049: ('SB-SEC250K-DN', 'Security Module'),
    5020: ('SB-ZMix23-DN', 'Zone Beast Mix23'),
}


class Device(object):
    list = []

    @staticmethod
    def append(device):
        if device not in Device.list:
            Device.list.append(device)
        else:
            raise Exception('Device already registered')

    @staticmethod
    def remove(device):
        if device in Device.list:
            Device.list.remove(device)
        else:
            raise Exception('Device not registered')

    @staticmethod
    def type_info(devtype):
        if devtype in TYPES:
            return TYPES[devtype]
        else:
            return ('Unknown', 'Unknown')

    def __init__(
        self, devtype=None, netid=None, devid=None, register=True
    ):
        self._devtype = devtype
        self.netid = netid
        self.devid = devid
        if register:
            self.register()
        self.receive_ready = Event()
        self.receive_ready.set()

    @property
    def devtype(self):
        return self._devtype

    @property
    def info(self):
        return self.type_info(self.devtype)

    def receive(self, packet):
        if (
            (self.netid is None or packet.netid in (self.netid, 255)) and
            (self.devid is None or packet.devid in (self.devid, 255))
        ):
            self.receive_ready.wait()
            self.receive_ready.clear()
            self.receive_func(packet)
            self.receive_ready.set()
        if packet.src_netid == self.netid and packet.src_devid == self.devid:
            self.receive_ready.wait()
            self.receive_ready.clear()
            self.send_func(packet)
            self.receive_ready.set()

    def receive_func(self, packet):
        pass

    def register(self):
        self.append(self)

    def send_func(self, packet):
        pass

    def unregister(self):
        self.remove(self)
