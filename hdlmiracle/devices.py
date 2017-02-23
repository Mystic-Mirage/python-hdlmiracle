from collections import OrderedDict

from .datatypes import DeviceAddress
from .helpers import Property, ReprMixin
from .packet import Packet


__all__ = [
    'Driver',
    'Emulator',
    'Imitator',
    'Monitor',
    'device_details',
]


DEVICE_TYPES = [
    (1,     'HDL-MD0610',       '6 channels 10A dimmable scene controller'),
    (2,     'HDL-MD1210A',      '12 channels 10A dimmable scene controller '
                                '(with load status feedback)'),
    (3,     'HDL-MD2405A',      '24 channels 5A dimmable scene controller '
                                '(with load status feedback)'),
    (4,     'HDL-MD0620',       '6 channels 20A dimmable scene controller'),
    (5,     'HDL-MD1210',       '12 channels 10A dimmable scene controller'),
    (6,     'HDL-MD2405',       '24 channels 5A dimmable scene controller'),
    (7,     'HDL-MDH1210A',     '12 channels 10A dimmable scene controller '
                                '(with load status feedback)'),
    (8,     'HDL-MD0620A',      '6 channels 20A dimmable scene controller '
                                '(with load status feedback)'),
    (9,     'HDL-MDH0610',      '6 channels 10A dimmable scene controller '
                                '(with load status feedback)'),
    (11,    'HDL-MR1220',       '12 channels 20A relay'),
    (12,    'HDL-MR2420',       '24 channels 20A relay'),
    (13,    'HDL-MC48IP',       '48 channels scene controller bus '
                                '(up to 8 unit 6 channels power modules '
                                'in which is extendable, standard t-shaped '
                                'tunnel installation with Ethernet channels)'),
    (14,    'HDL-MC48',         '48 channels scene controller bus '
                                '(up to 8 unit 6 channel power modules '
                                'in which is extendible, standard t-shaped '
                                'tunnel installation)'),
    (15,    'HDL-MD0602',       '6 channels 2A dimmable scene controller'),
    (16,    'HDL-MC48IPDMX',    '48 channels scene controller bus '
                                '(standard t-shaped tunnel installation '
                                'with Ethernet channels, with DMX)'),
    (17,    'HDL-MRDA06',       '6 channels, 0-10V output, dimmable scene '
                                'controller of fluorescent lamp'),
    (18,    'HDL-MC48DMX',      '48 channels scene controller bus (standard '
                                't-shaped tunnel installation with DMX)'),
    (19,    'HDL-MR1210',       '12 channels 10A relay'),
    (20,    'HDL-MC240IP',      '240 channels show controller'),
    (21,    'HDL-MC512IP',      '512 channels show controller'),
    (22,    'HDL-MR1205',       '12 channels 5A relay'),
    (23,    'HDL-MR0810',       '8 channels 10A relay'),
    (25,    'HDL-MD0403',       '4 channels 3A dimmable scene controller'),
    (26,    'HDL-MDH2405',      '24 channels 5A dimmable scene controller'),
    (27,    'HDL-MDH0620',      '6 channels 20A dimmable scene controller'),
    (28,    'HDL-MD0304',       '3 channels 4A dimmable scene controller'),
    (32,    'SB-DMX48-DN',      'DMX48'),
    (40,    'HDL-MC48DALI',     '48 channels DALI scene controller'),
    (50,    'HDL-MP8RM',        '8 keys multi-functional panel '
                                '(with infrared control)'),
    (51,    'HDL-MP8M',         '8 keys multi-functional panel'),
    (52,    'HDL-MP4RM',        '4 keys multi-functional panel '
                                '(with infrared control)'),
    (53,    'HDL-MP4M',         '4 keys multi-functional panel'),
    (54,    'HDL-MP6R',         '6 keys scene panel (with infrared control, '
                                'scene intensity temporary adjustable)'),
    (55,    'HDL-MP6',          '6 keys scene panel (without infrared control, '
                                'with scene intensity temporary adjustable)'),
    (56,    'HDL-MP2R',         '2 keys scene panel (with infrared control, '
                                'scene intensity temporary adjustable)'),
    (57,    'HDL-MP2',          '2 keys scene panel (without infrared control, '
                                'with scene intensity temporary adjustable)'),
    (60,    'HDL-MP8RM',        '8 keys multi-functional panel '
                                '(with infrared control)'),
    (61,    'HDL-MP4RM',        '4 keys multi-functional panel '
                                '(with infrared control)'),
    (62,    'HDL-MWL16',        'Wireless receiver'),
    (63,    'HDL-MP4RM',        '4 keys multi-functional panel '
                                '(with infrared control)'),
    (70,    'HDL-MSR04',        'Room partition'),
    (80,    'HDL-MS01R',        'Motion sensor'),
    (81,    'HDL-MS01L',        'Linear sensor'),
    (90,    'HDL-MS01R',        'Motion sensor'),
    (91,    'HDL-MS01L',        'Linear sensor'),
    (92,    'HDL-MS12',         '12 channels sensor'),
    (93,    'HDL-MS04',         'Sensor Input Module'),
    (95,    'HDL-MHS01',        'Roof-Mounting Infrared '
                                'Dual-Technology Motion Sensor'),
    (96,    'HDL-MPE01',        'Ambient Intensity Monitor'),
    (97,    'HDL-MHS02',        'Wide Field Infrared '
                                'Dual-Technology Motion Sensor'),
    (98,    'HDL-MHS02',        'Wide Field Infrared '
                                'Dual-Technology Motion Sensor'),
    (99,    'HDL-MHS01',        'Roof-Mounting Infrared '
                                'Dual-Technology Motion Sensor'),
    (100,   'HDL-MT12IP',       '12 channels timer (standard t-shaped tunnel '
                                'installation with Ethernet port)'),
    (101,   'HDL-MT12IP',       '12 channels timer (standard t-shaped tunnel '
                                'installation with Ethernet port)'),
    (102,   'HDL-MT01',         '1 channels Event timer'),
    (103,   'HDL-MT12IP',       '12 channels timer (standard t-shaped tunnel '
                                'installation with Ethernet port)'),
    (112,   'SB-DN-HVAC',       'HVAC Module'),
    (118,   'SB-4Z-UN',         '4 Zone Dry Contact'),
    (128,   'HDL-MBUS-RS232',   'HDL-BUS/RS232 converter'),
    (149,   'SB-DDP-EU',        'Dynamic Display Panel'),
    (150,   'HDL-MR1220A',      '12 channels 20A relay'),
    (151,   'HDL-MR2420A',      '24 channels 20A relay '
                                'without status feedback'),
    (152,   'HDL-MR0610',       '6 channels 10A relay'),
    (153,   'HDL-MR0416A',      '4 channels 16A relay'),
    (236,   'HDL-MBUS01IP',     '1 port switchboard'),
    (237,   'HDL-MBUS04IP',     '4 port switchboard'),
    (238,   'HDL-MBUS08IP',     '8 port switchboard'),
    (278,   'SB-3BS-EU',        '3 Buttons'),
    (281,   'SB-6BS-EU',        '6 Buttons'),
    (282,   'SB-4BS-EU',        '4 Buttons'),
    (300,   'HDL-MIR01',        'Infrared signal emission,'
                                'remote receiving module'),
    (306,   'SB-IR-UN',         'IR Emitter'),
    (309,   'SB-9in1T-CL',      '9 in 1 sensor'),
    (313,   'SB-6in1TL-CL',     '6 in 1 sensor'),
    (314,   'SB-5in1TL-CL',     '5 in 1 sensor'),
    (400,   'HDL-MAIR01',       'Air-Condition controller'),
    (428,   'SB-RLY8c16A-DN',   'Relay 8ch 16A'),
    (434,   'SB-RLY4c20A-DN',   'Relay 4ch 20A'),
    (500,   'HDL-MTS7000',      '7" True Color Touch Screen'),
    (600,   'SB-DIM6c2A-DN',    'Dimmer 6ch 2A'),
    (601,   'SB-DIM4c3A-DN',    'Dimmer 4ch 3A'),
    (602,   'SB-DIM2c6A-DN',    'Dimmer 2ch 6A'),
    (700,   'HDL-MW02',         'Curtain controller'),
    (701,   'HDL-MW02',         'Curtain controller'),
    (800,   'HDL-MDMXI08',      '8 channels DMX input module'),
    (850,   'HDL-MC96IPDMX',    '96 channels scene controller bus (standard '
                                't-shaped tunnel installation with DMX)'),
    (898,   'SB-4LED-DCV',      'LED Dimmer 4ch'),
    (900,   'HDL-MPM01',        'Digital electric meter'),
    (902,   'SB-ZAudio2-DN',    'Zone Audio'),
    (1000,  'HDL-MBUS-EIB',     'EIB/HDL-BUS converter'),
    (1005,  'HDL-MBUS-SAMSUNG', 'SAMSUNG touch screen convert to HDL-BUS'),
    (1108,  'SB-Logic2-DN',     'Logic Module'),
    (1201,  'SB-RSIP-DN',       'RS232IP Module'),
    (3049,  'SB-SEC250K-DN',    'Security Module'),
    (5020,  'SB-ZMix23-DN',     'Zone Beast Mix23'),
]


def device_details(device_type):
    device_types = {t: (m, d) for t, m, d in DEVICE_TYPES}
    return device_types.get(device_type, ('Unknown', 'Unknown'))


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
