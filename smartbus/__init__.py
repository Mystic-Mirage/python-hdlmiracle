from __future__ import absolute_import

from ._device import Device, TYPES
from ._opcode import (
    OC_CHANNEL_CONTROL,
    OC_CHANNEL_CONTROL_R,
    OC_CHANNELS_REPORT,
    OC_CHANNELS_STATUS,
    OC_CHANNELS_STATUS_R,
    OC_SEARCH,
    OC_SEARCH_R,
)
from ._packet import (
    ALL_DEVICES,
    ALL_NETWORKS,
    CREEPYFROG,
    HDLMIRACLE,
    HEADERS,
    SMARTCLOUD,
    BusFromStream,
    BusPacket,
    Packet
)


__all__ = [
    'ALL_DEVICES',
    'ALL_NETWORKS',
    'CREEPYFROG',
    'HDLMIRACLE',
    'HEADERS',
    'OC_CHANNEL_CONTROL',
    'OC_CHANNEL_CONTROL_R',
    'OC_CHANNELS_REPORT',
    'OC_CHANNELS_STATUS',
    'OC_CHANNELS_STATUS_R',
    'OC_SEARCH',
    'OC_SEARCH_R',
    'SMARTCLOUD',
    'TYPES',
    'BusFromStream',
    'BusPacket',
    'Device',
    'Packet',
    'init',
    'quit',
    'sendmethod',
]


distrubutor = None
receiver = None
sender = None


def init(header=None, src_ipaddress=None, no_sender=False):
    from ._handle import Distributor, Receiver

    global device_list, distributor, pause, receiver, resume, sender

    if header:
        Packet.header = header

    if src_ipaddress:
        Packet.src_ipaddress = src_ipaddress

    device_list = Device.list

    receiver = Receiver()
    receiver.daemon = True
    receiver.start()

    distributor = Distributor(receiver, device_list)
    distributor.daemon = True
    distributor.start()

    if not no_sender:
        from ._handle import Sender
        global send, sendmethod
        sender = Sender()
        send = sender.put
        sender.daemon = True
        sender.start()


def pause():
    global distributor
    if distributor:
        distributor.pause()


def resume():
    global distrubutor
    if distributor:
        distributor.resume()


def sendmethod(func):
    global device_list, send, sender

    def wrapper(obj, *args, **kwargs):
        if sender and obj in device_list:
            return send(func(obj, *args, **kwargs))
    return wrapper


def quit():
    global device_list, distributor, receiver, send, sender

    receiver.stop()
    receiver.join()

    distributor.stop()
    distributor.join()

    del device_list
    del receiver
    del distributor

    if sender:
        sender.stop()
        sender.join()

        del sender
        del send


del absolute_import
