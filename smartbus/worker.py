from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport
from future import standard_library  # @UnusedImport

from queue import Empty, Queue
from socket import socket, timeout
import sqlite3
from threading import Event, Thread

from .packet import Packet


class Receiver(Thread):

    def get(self):
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    def run(self):
        self.exit = Event()
        self.queue = Queue()

        sock = socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1)
        sock.bind(('', 6000))

        while not self.exit.is_set():
            try:
                raw_packet = sock.recv(2048)
            except timeout:
                pass
            else:
                self.queue.put(raw_packet)

        sock.close()

    def stop(self):
        self.exit.set()


class Packeter(Thread):

    def put(self, packet):
        self.queue.put('INSERT ')

    def run(self):
        self.exit = Event()
        self.queue = Queue()

        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            'CREATE TABLE packets ('
            'id INTEGER PRIMARY KEY, '
            'src_netid, '
            'src_devid, '
            'src_devtype, '
            'op_code, '
            'dst_netid, '
            'dst_devid, '
            'data, '
            'source_ip, '
            'big BOOLEAN, '
            'hdlmiracle BOOLEAN, '
            'timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, '
            ')'
        )

        self.connection.close()

    def stop(self):
        self.exit.set()


class Parser(Thread):

    def __init__(self, packeter, receiver):
        super().__init__()
        self.receiver = receiver
        self.packeter = packeter

    def run(self):
        self.exit = Event()

        while not self.exit.is_set():
            raw_packet = self.receiver.get()
            if raw_packet is not None:
                self.packeter.put(Packet(raw_packet))

    def stop(self):
        self.exit.set()


class Worker(object):

    def __init__(self):
        self.receiver = Receiver()
        self.packeter = Packeter()
        self.parser = Parser(self.packeter, self.receiver)

    def start(self):
        self.receiver.start()
        self.packeter.start()
        self.parser.start()

    def stop(self):
        self.receiver.stop()
        self.packeter.stop()
        self.parser.stop()
