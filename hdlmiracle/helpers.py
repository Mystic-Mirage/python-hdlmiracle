from sys import version_info
from threading import Lock, Thread


__all__ = [
    'PY2',
    'PY3',
    'Property',
    'ReprMixin',
    'call_lock',
    'spawn',
]


PY2 = version_info[0] == 2
PY3 = version_info[0] == 3


class Property(object):

    def __init__(self, default):
        self.default = default

    def name(self, instance):
        return '__{0}_{1}'.format(id(self), id(instance))

    def __get__(self, instance, owner=None):
        return getattr(instance, self.name(instance), self.default)

    def __set__(self, instance, value):
        if value is None:
            return
        setattr(instance, self.name(instance), self.default.__class__(value))


class ReprMixin(object):

    def dict(self):
        return {}

    def __repr__(self):
        args = ['{0}={1}'.format(k, repr(v)) for k, v in self.dict().items()]
        args = ', '.join(args)
        return '{module}.{name}({args})'.format(
            module=self.__class__.__module__,
            name=self.__class__.__name__,
            args=args,
        )


def call_lock(obj, func_name, args=None, kwargs=None, callback=None):
    if hasattr(obj, func_name):
        func = getattr(obj, func_name)
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        func_lock_name = '__{func_name}_lock'.format(func_name=func_name)
        if hasattr(obj, func_lock_name):
            func_lock = getattr(obj, func_lock_name)
        else:
            func_lock = Lock()
            setattr(obj, func_lock_name, func_lock)
        func_lock.acquire()
        try:
            response = func(*args, **kwargs)
            if callback and response is not None:
                callback(response)
        finally:
            func_lock.release()


def spawn(target, *args, **kwargs):
    thread = Thread(target=target, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread
