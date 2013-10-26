from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport
from future import standard_library  # @UnusedImport

from queue import Empty, Queue
import socket
from threading import Thread

from .device import Device
from .packet import Packet


class Receiver(Thread):

    def get(self, block=True, timeout=None):
        try:
            return self.queue.get(block, timeout)
        except Empty:
            return None

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


class Parser(Thread):

    def __init__(self, receiver, device_list):
        super().__init__()
        self.receiver = receiver
        self.device_list = device_list

    def run(self):
        self.running = True

        while self.running:
            raw_packet = self.receiver.get_nowait()
            if raw_packet is not None:
                for d in self.device_list:
                    d.receive(Packet(raw_packet))

    def stop(self):
        self.running = False


class Worker(object):

    def __init__(self):
        self.receiver = Receiver()
        self.parser = Parser(self.receiver, Device.list)

    def start(self):
        self.receiver.start()
        self.parser.start()

    def stop(self):
        self.receiver.stop()
        self.parser.stop()
