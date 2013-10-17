from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport
from future import standard_library  # @UnusedImport

from queue import Queue  # @UnresolvedImport
import sys

from .workers import Listener, Parser


def _module():
    return sys.modules[__name__.rpartition('.')[0]]


def init():
    queue = Queue()
    listener = Listener(queue)
    parser = Parser(queue)

    module = _module()
    setattr(module, 'listener', listener)
    setattr(module, 'parser', parser)

    parser.start()
    listener.start()


def quit():  # @ReservedAssignment
    from . import listener  # @UnresolvedImport
    listener.stop()  # @UndefinedVariable

    module = _module()
    delattr(module, 'listener')
    delattr(module, 'parser')
