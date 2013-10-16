from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport
from future import standard_library  # @UnusedImport

from queue import Queue  # @UnresolvedImport
import sys

from .listener import Listener
from .parser import Parser


def init():
    queue = Queue()
    listener = Listener(queue)
    parser = Parser(queue)

    module_obj = sys.modules[__name__.rpartition('.')[0]]
    setattr(module_obj, 'listener', listener)
    setattr(module_obj, 'parser', parser)

    parser.start()
    listener.start()


def quit_():
    from smartbus import listener
    listener.stop()  # @UndefinedVariable
