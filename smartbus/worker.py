from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport
from future import standard_library  # @UnusedImport

from queue import Queue
import socket
from threading import Event, Thread


class _Listener(Thread):

    def __init__(self, lp_queue, timeout=1):
        super().__init__()
        self.lp_queue = lp_queue
        self.timeout = timeout
        self.exit = Event()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(self.timeout)
        sock.bind(('', 6000))

        while not self.exit.is_set():
            try:
                raw_packet = sock.recv(2048)
            except:
                pass
            else:
                self.lp_queue.put(raw_packet)

        self.lp_queue.put(None)
        sock.close()

    def stop(self):
        self.exit.set()


class _Parser(Thread):

    def __init__(self, lp_queue, pp_queue):
        super().__init__()
        self.lp_queue = lp_queue
        self.pp_queue = pp_queue
        self.exit = Event()

    def run(self):
        while not self.exit.is_set():
            raw_packet = self.lp_queue.get()
            if raw_packet is None:
                break
            print(raw_packet)

    def stop(self):
        self.exit.set()


class Worker(object):

    def __init__(self):
        self.lp_queue = Queue()
        self.pp_queue = Queue()
        self.listener = _Listener(self.lp_queue)
        self.parser = _Parser(self.lp_queue, self.pp_queue)

    def start(self):
        self.parser.start()
        self.listener.start()

    def stop(self):
        self.listener.stop()
        self.parser.stop()
