from ._device import Device, TYPES, device_list
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
    Header,
    Packet,
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
    'Device',
    'Header',
    'Packet',
    'device_list',
    'init',
    'quit',
    'sendmethod',
]


Header.__module__ = __name__
Packet.__module__ = __name__


distrubutor = None
receiver = None
sender = None


def init(header=None, src_ipaddress=None, no_sender=False):
    from ._handle import Distributor, Receiver

    global distributor, receiver

    if header:
        Packet.header = header

    if src_ipaddress:
        Packet.src_ipaddress = src_ipaddress

    receiver = Receiver()
    receiver.daemon = True
    receiver.start()

    distributor = Distributor(receiver, device_list)
    distributor.daemon = True
    distributor.start()

    if not no_sender:
        from ._handle import Sender
        global send, sender
        sender = Sender()
        send = sender.put
        sender.daemon = True
        sender.start()


def pause():
    if distributor:
        distributor.pause()


def resume():
    if distributor:
        distributor.resume()


def send(_):
    pass


def sendmethod(func):
    def wrapper(obj, *args, **kwargs):
        if sender and obj in device_list:
            return send(func(obj, *args, **kwargs))
    return wrapper


def quit():
    receiver.stop()
    receiver.join()

    distributor.stop()
    distributor.join()

    if sender:
        sender.stop()
        sender.join()
