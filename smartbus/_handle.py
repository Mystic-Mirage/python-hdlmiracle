from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *
from future import standard_library

from queue import Empty, Queue
import socket
from threading import Thread

from ._packet import Packet


class Distributor(Thread):

    def __init__(self, receiver, device_list):
        super().__init__()
        self.receiver = receiver
        self.device_list = device_list

    def run(self):
        self.running = True

        while self.running:
            try:
                raw_packet = self.receiver.get(timeout=1)
            except Empty:
                pass
            else:
                if raw_packet is not None:
                    for device in self.device_list:
                        device.receive(Packet(raw_packet))

    def stop(self):
        self.running = False


class Receiver(Thread):

    def get(self, block=True, timeout=None):
        return self.queue.get(block, timeout)

    def get_nowait(self):
        return self.get(False)

    def run(self):
        self.queue = Queue()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1)
        sock.bind(('', 6000))

        self.running = True

        while self.running:
            try:
                raw_packet = sock.recv(2048)
            except socket.timeout:
                pass
            else:
                self.queue.put(raw_packet)

        sock.close()

    def stop(self):
        self.running = False


class Sender(Thread):

    def put(self, value):
        self.queue.put(value)

    def run(self):
        self.queue = Queue()

        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.running = True

        while self.running:
            try:
                packet = self.queue.get(timeout=1)
            except socket.timeout:
                pass
            except Empty:
                pass
            else:
                sock.sendto(packet.packed, ('<broadcast>', 6000))

        sock.close()

    def stop(self):
        self.running = False
