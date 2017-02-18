from collections import defaultdict
from time import sleep

from socket import SOL_SOCKET, SO_BROADCAST, error as SocketError
try:
    from SocketServer import BaseRequestHandler, ThreadingUDPServer
except ImportError:
    from socketserver import BaseRequestHandler, ThreadingUDPServer

from .exceptions import HDLMiracleIPBusException
from .helpers import Property, call_lock, spawn
from .packet import ALL_DEVICES, ALL_NETWORKS, IPPacket


__all__ = [
    'Bus',
    'IPBus',
]


IP_PORT = 6000


class DeviceSet(object):

    def __init__(self, devices=None):
        self._devices = defaultdict(set)
        if devices:
            for device in devices:
                self.add(device)

    def _set_control(self, action, device):
        for network_id in [device.subnet_id, ALL_NETWORKS]:
            for device_id in [device.device_id, ALL_DEVICES]:
                _set = self._devices[network_id, device_id]
                try:
                    getattr(_set, action)(device)
                except (AttributeError, KeyError):
                    pass

    def add(self, device):
        self._set_control('add', device)

    def remove(self, device):
        self._set_control('remove', device)

    def __eq__(self, other):
        return set(self) == set(other)

    def __getitem__(self, y):
        return self._devices[y]

    def __iter__(self):
        return iter(self[ALL_NETWORKS, ALL_DEVICES])

    def __repr__(self):
        devices_repr = ', '.join(repr(device) for device in self)
        return '{module}.{name}([{devices}])'.format(
            module=self.__class__.__module__,
            name=self.__class__.__name__,
            devices=devices_repr,
        )


class Bus(object):
    devices = Property(DeviceSet())
    running = Property(False)

    def __init__(self, devices=None):
        if devices:
            for device in devices:
                self.attach(device)

    def attach(self, device):
        if (hasattr(device, 'send') and
                self.send_wrapper not in getattr(device.send, 'wrappers', [])):
            device.send = self.send_wrapper(device.send)
        self.devices.add(device)

    def detach(self, device):
        self.devices.remove(device)
        if (hasattr(device, 'send') and
                self.send_wrapper in getattr(device.send, 'wrappers', [])):
            wrappers = device.send.wrappers
            wrappers.remove(self.send_wrapper)
            device.send = device.send.orig
            for wrapper in wrappers:
                device.send = wrapper(device.send)

    def recv(self, packet):
        if not self.running:
            return

        for device in self.devices[packet.address]:
            spawn(call_lock, device, 'catch', args=(packet,))

        for target_device in self.devices[packet.target_address]:
            spawn(call_lock, target_device, 'receive', args=(packet,),
                  callback=self.send)

    def send(self, packet):
        pass

    def send_wrapper(self, send):
        def sender(*args, **kwargs):
            packet = send(*args, **kwargs)
            spawn(self.send, packet)
            return packet

        sender.wrappers = getattr(send, 'wrappers', [])
        sender.wrappers.append(self.send_wrapper)
        sender.orig = getattr(send, 'orig', send)
        return sender

    def serve(self):
        self.running = True
        try:
            while self.running:
                for device in self.devices:
                    spawn(call_lock, device, 'heartbeat', callback=self.send)
                sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False

    def start(self):
        spawn(self.serve)

    def stop(self):
        self.running = False


class IPHandler(BaseRequestHandler):

    def handle(self):
        data, _ = self.request
        packet = IPPacket(data)
        self.server.recv(packet)


class IPServer(ThreadingUDPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, request_handler, recv_func):
        ThreadingUDPServer.__init__(self, server_address, request_handler)
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.recv = recv_func


class IPBus(Bus):
    ipaddress = Property(IPPacket.ipaddress)
    head = Property(IPPacket.head)
    strict = Property(True)

    def __init__(self, devices=None, ipaddress=None, head=None, strict=None):
        Bus.__init__(self, devices=devices)
        self.ipaddress = ipaddress
        self.head = head
        self.strict = strict
        self.socket_server = IPServer(('', IP_PORT), IPHandler, self.recv)

    def recv(self, packet):
        if self.strict and packet.head != self.head:
            return
        Bus.recv(self, packet)

    def send(self, packet):
        packet = IPPacket(packet)
        packet.ipaddress = self.ipaddress
        packet.head = self.head
        data = bytes(packet)
        try:
            self.socket_server.socket.sendto(data, ('<broadcast>', IP_PORT))
        except SocketError as err:
            raise HDLMiracleIPBusException(
                'Error sending IPPacket: {err}'.format(err=err)
            )

    def serve(self):
        spawn(self.socket_server.serve_forever)
        Bus.serve(self)

    def stop(self):
        self.socket_server.shutdown()
        Bus.stop(self)
