from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport
from future import standard_library  # @UnusedImport

from queue import Empty, Queue
import socket
import sqlite3
from threading import Thread

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


class Packeter(Thread):

    def put(self, packet):
        columns = [
            'src_netid',
            'src_devid',
            'src_devtype',
            'op_code',
            'dst_netid',
            'dst_devid',
            'data',
            'source_ip',
            'big',
            'hdlmiracle',
        ]
        c_names = ', '.join(columns)
        values = ', '.join([':{}'.format(c) for c in columns])
        self.queue.put((
            'INSERT INTO packets ({0}) VALUES ({1})'.format(c_names, values),
            {
                'src_netid': packet.src_netid,
                'src_devid': packet.src_devid,
                'src_devtype': packet.src_devtype,
                'op_code': packet.op_code,
                'dst_netid': packet.dst_netid,
                'dst_devid': packet.dst_devid,
                'data': sqlite3.Binary(packet.data),
                'source_ip': packet.source_ip.compressed,
                'big': packet.big,
                'hdlmiracle': packet.hdlmiracle
            },
            None
        ))

    def run(self):
        self.queue = Queue()

        connection = sqlite3.connect(':memory:')
        cursor = connection.cursor()

        columns = [
            'id INTEGER PRIMARY KEY',
            'src_netid TINYINT',
            'src_devid TINYINT',
            'src_devtype SMALLINT',
            'op_code SMALLINT',
            'dst_netid TINYINT',
            'dst_devid TINYINT',
            'data BLOB',
            'source_ip TEXT',
            'big BOOLEAN',
            'hdlmiracle BOOLEAN',
            'timestamp DATETIME DEFAULT CURRENT_TIMESTAMP',
        ]

        cursor.execute(
            'CREATE TABLE packets ({})'.format(', '.join(columns))
        )

        self.running = True

        while self.running:
            try:
                req, args, res = self.queue.get_nowait()
            except Empty:
                continue
            cursor.execute(req, args)
            if res is not None:
                for i in cursor:
                    print(i)

        connection.close()

    def select_all(self):
        self.queue.put(('SELECT * FROM packets', (), ''))

    def stop(self):
        self.running = False


class Parser(Thread):

    def __init__(self, packeter, receiver):
        super().__init__()
        self.receiver = receiver
        self.packeter = packeter

    def run(self):
        self.running = True

        while self.running:
            raw_packet = self.receiver.get_nowait()
            if raw_packet is not None:
                self.packeter.put(Packet(raw_packet))

    def stop(self):
        self.running = False


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
