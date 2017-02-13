from collections import OrderedDict

from hdlmiracle.datatypes import DeviceAddress
from hdlmiracle.helpers import Property, ReprMixin
from hdlmiracle.packet import Packet


__all__ = [
    'Driver',
    'Emulator',
    'Imitator',
    'Monitor',
    'device_details',
]


DEVICE_TYPES = {
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


def device_details(device_type):
    return DEVICE_TYPES.get(device_type, ('Unknown', 'Unknown'))


class BaseDevice(ReprMixin):
    subnet_id = Property(Packet.target_subnet_id)
    device_id = Property(Packet.target_device_id)

    def __init__(self, subnet_id=None, device_id=None):
        self.subnet_id = subnet_id
        self.device_id = device_id

    @property
    def address(self):
        return DeviceAddress(subnet_id=self.subnet_id, device_id=self.device_id)

    @address.setter
    def address(self, device_address):
        self.subnet_id, self.device_id = device_address

    def dict(self):
        _dict = OrderedDict()
        _dict['subnet_id'] = self.subnet_id
        _dict['device_id'] = self.device_id
        return _dict


class Controller(BaseDevice):

    def packet(self, **kwargs):
        kwargs.update(
            target_subnet_id=self.subnet_id,
            target_device_id=self.device_id,
        )
        return Packet(**kwargs)

    def send(self, *args, **kwargs):
        pass


class Imitator(BaseDevice):
    subnet_id = Property(Packet.subnet_id)
    device_id = Property(Packet.device_id)
    device_type = Property(Packet.device_type)

    def __init__(self, subnet_id=None, device_id=None, device_type=None):
        BaseDevice.__init__(self, subnet_id=subnet_id, device_id=device_id)
        self.device_type = device_type

    def dict(self):
        _dict = BaseDevice.dict(self)
        _dict['device_type'] = self.device_type
        return _dict

    def heartbeat(self):
        pass

    def packet(self, **kwargs):
        kwargs.update(
            subnet_id=self.subnet_id,
            device_id=self.device_id,
            device_type=self.device_type,
        )
        return Packet(**kwargs)

    def send(self, *args, **kwargs):
        pass


class Monitor(BaseDevice):

    def catch(self, packet):
        pass

    def receive(self, packet):
        pass


class Driver(Controller, Monitor):
    pass


class Emulator(Imitator, Monitor):
    pass
