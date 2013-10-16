from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport

from threading import Thread


class Parser(Thread):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def run(self):
        while True:
            raw_packet = self.queue.get()
            if raw_packet is None:
                break
            print(raw_packet)
