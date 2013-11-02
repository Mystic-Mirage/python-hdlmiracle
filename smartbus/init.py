from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *

import sys

from .device import Device
from .handle import Distributor, Receiver, Sender


def _module():
    return sys.modules[__name__.rpartition('.')[0]]


def init():
    device_list = Device.list

    receiver = Receiver()
    sender = Sender()
    distributor = Distributor(receiver, device_list)

    receiver.start()
    sender.start()
    distributor.start()

    setattr(_module(), 'device_list', device_list)
    setattr(_module(), 'receiver', receiver)
    setattr(_module(), 'sender', sender)
    setattr(_module(), 'distributor', distributor)
    setattr(_module(), 'send', sender.put)


def quit():
    from . import receiver, sender, distributor

    receiver.stop()
    sender.stop()
    distributor.stop()

    receiver.join()
    sender.join()
    distributor.join()

    delattr(_module(), 'device_list')
    delattr(_module(), 'receiver')
    delattr(_module(), 'sender')
    delattr(_module(), 'distributor')
    delattr(_module(), 'send')
