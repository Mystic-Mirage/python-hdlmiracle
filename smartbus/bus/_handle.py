from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *
from future import standard_library

from queue import Empty, Queue
from serial import Serial
from threading import Thread

from .._packet import BusFromStream


class Bus(object):

    def __init__(self, port, timeout=1, direction_in=None, direction_out=None):
        self.serial = Serial(port, timeout=1)
        self.direction_in = direction_in
        self.direction_out = direction_out
        if self.direction_in is not None:
            self.direction_in()

    def recv(self):
        bus_packet = BusFromStream()
        while True:
            char = self.serial.read(1)
            if char == b'':
                return None
            bus_packet.send(char)
            if bus_packet.length is not None:
                break
        bus_packet.extend(self.serial.read(bus_packet.length))
        return bus_packet

    def send(self, data):
        if self.direction_out is not None:
            self.direction_out()
        self.serial.write(data)
        if self.direction_in is not None:
            self.direction_in()

    def close(self):
        self.serial.close()


class Distributor(Thread):

    def __init__(self, receiver, device_list):
        super().__init__()
        self.receiver = receiver
        self.device_list = device_list

    def run(self):
        self.running = True

        while self.running:
            try:
                bus_packet = self.receiver.get(timeout=1)
            except Empty:
                pass
            else:
                if bus_packet is not None:
                    packet = bus_packet.get()
                    if packet is not None:
                        for device in self.device_list:
                            device.receive(packet)

    def stop(self):
        self.running = False


class Receiver(Thread):

    def __init__(self, bus):
        super().__init__()
        self.bus = bus

    def get(self, block=True, timeout=None):
        return self.queue.get(block, timeout)

    def get_nowait(self):
        return self.get(False)

    def run(self):
        self.queue = Queue()

        self.running = True

        while self.running:
            bus_packet = self.bus.recv()
            self.queue.put(bus_packet)

    def stop(self):
        self.running = False


class Sender(Thread):

    def __init__(self, bus):
        super().__init__()
        self.bus = bus

    def put(self, value):
        self.queue.put(value)

    def run(self):
        self.queue = Queue()

        self.running = True

        while self.running:
            try:
                packet = self.queue.get(timeout=1)
            except Empty:
                pass
            else:
                self.bus.send(packet.packed())

    def stop(self):
        self.running = False
