from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from future.builtins import *  # @UnusedWildImport
from future import standard_library  # @UnusedImport

import sys

from .worker import Worker


def _module():
    return sys.modules[__name__.rpartition('.')[0]]


def init():

    worker = Worker()
    worker.start()

    setattr(_module(), 'worker', worker)


def quit():  # @ReservedAssignment
    from . import worker  # @UnresolvedImport
    worker.stop()  # @UndefinedVariable

    delattr(_module(), 'worker')
