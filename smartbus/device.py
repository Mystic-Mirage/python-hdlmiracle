from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *


class Device(object):
    list = []

    def __init__(self, net_id=255, dev_id=255, dev_type=0, register=True):
        self.net_id = net_id
        self.dev_id = dev_id
        self.dev_type = dev_type
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

    def receive(self, packet):
        pass

    def register(self):
        self.append(self)

    def unregister(self):
        self.remove(self)
