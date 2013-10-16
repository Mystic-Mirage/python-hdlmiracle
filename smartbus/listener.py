from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport
from future import standard_library  # @UnusedImport

import socket
from threading import Event, Thread


class Listener(Thread):

    def __init__(self, queue, timeout=1):
        super().__init__()
        self.queue = queue
        self.timeout = timeout
        self.exit = Event()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(self.timeout)
        sock.bind(('', 6000))

        while True:
            try:
                raw_packet = sock.recv(2048)
            except:
                pass
            else:
                self.queue.put(raw_packet)
            if self.exit.is_set():
                break

        self.queue.put(None)
        sock.close()

    def stop(self):
        self.exit.set()
