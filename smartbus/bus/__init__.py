from ._device import Device


def init(port, timeout=1, direction_in=None, direction_out=None):
    from ._handle import Bus, Distributor, Receiver, Sender

    global bus, device_list, distributor, receiver, send, sender

    device_list = Device.list

    bus = Bus(port, timeout, direction_in, direction_out)
    receiver = Receiver(bus)
    sender = Sender(bus)
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
    global bus, device_list, distributor, receiver, send, sender

    bus.close()
    receiver.stop()
    sender.stop()
    distributor.stop()

    receiver.join()
    sender.join()
    distributor.join()

    del bus
    del device_list
    del receiver
    del sender
    del distributor
    del send
