from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport


class Device(object):

    list = []

    def __init__(self, net_id=255, dev_id=255, dev_type=0):
        self.net_id = net_id
        self.dev_id = dev_id
        self.dev_type = dev_type

    @classmethod
    def append(cls, device):
        cls.list.append(device)

    @classmethod
    def remove(cls, device):
        cls.list.remove(device)

    def receive(self, packet):
        pass

    def register(self):
        self.append(self)

    def unregister(self):
        self.remove(self)
