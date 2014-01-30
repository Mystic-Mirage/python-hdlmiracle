from __future__ import absolute_import

from ._device import Device, TYPES
from ._opcode import (
    OC_CHANNELS_REPORT,
    OC_CHANNELS_STATUS,
    OC_CHANNELS_STATUS_R,
    OC_SEARCH,
    OC_SEARCH_R,
)
from ._packet import ALL_DEVICES, ALL_NETWORKS, Packet


__all__ = [
    'ALL_DEVICES',
    'ALL_NETWORKS',
    'Device',
    'init',
    'OC_CHANNELS_REPORT',
    'OC_CHANNELS_STATUS',
    'OC_CHANNELS_STATUS_R',
    'OC_SEARCH',
    'OC_SEARCH_R',
    'Packet',
    'sendmethod',
    'TYPES',
    'quit',
]


def init():
    from ._handle import Distributor, Receiver, Sender

    global device_list, distributor, receiver, send, sender

    device_list = Device.list

    receiver = Receiver()
    sender = Sender()
    distributor = Distributor(receiver, device_list)

    send = sender.put

    receiver.daemon = True
    sender.daemon = True
    distributor.daemon = True

    receiver.start()
    sender.start()
    distributor.start()


def sendmethod(func):
    global device_list, send

    def wrapper(obj, *args, **kwargs):
        if obj in device_list:
            return send(func(obj, *args, **kwargs))
    return wrapper


def quit():
    global device_list, distributor, receiver, send, sender

    receiver.stop()
    sender.stop()
    distributor.stop()

    receiver.join()
    sender.join()
    distributor.join()

    del device_list
    del receiver
    del sender
    del distributor
    del send


del absolute_import
