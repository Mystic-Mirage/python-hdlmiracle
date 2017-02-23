from collections import Iterable, namedtuple

from .exceptions import HDLMiracleIPAddressError
from .helpers import PY3


__all__ = [
    'DeviceAddress',
    'Head',
    'HexArray',
    'HexByte',
    'HexWord',
    'IPAddress',
]


DeviceAddress = namedtuple('DeviceAddress', ['subnet_id', 'device_id'])


class Head(str):

    def __new__(cls, x):
        x = x[:10].ljust(10)
        isinstance(x, str) and x.encode('latin-1')
        if PY3 and isinstance(x, (bytearray, bytes)):
            x = str(x, 'latin-1')
        self = str.__new__(cls, x)
        return self

    def __iter__(self):
        return iter(self.encode('latin-1'))

    def __repr__(self):
        return repr(self.strip())


class HexArray(bytearray):

    def __init__(self, x=0):
        if PY3 and isinstance(x, str):
            bytearray.__init__(self, x, 'latin-1')
        elif isinstance(x, Iterable):
            l = []
            for i in x:
                if isinstance(i, Iterable):
                    l.extend(i)
                elif i is None:
                    pass
                else:
                    l.append(i)
            bytearray.__init__(self, l)
        else:
            bytearray.__init__(self, x)

    def append(self, x):
        if isinstance(x, Iterable):
            bytearray.extend(self, x)
        else:
            bytearray.append(self, x)

    def ascii(self):
        return ''.join(byte.chr() for byte in self)

    def step(self, step=8):
        for i in range(0, len(self), step):
            yield HexArray(self[i:i+step])

    def __eq__(self, other):
        return bytearray.__eq__(self, bytearray(other))

    def __getitem__(self, y):
        if isinstance(y, slice):
            return HexArray(bytearray.__getitem__(self, y))
        return HexByte(bytearray.__getitem__(self, y))

    def __iter__(self):
        return iter(HexByte(byte) for byte in bytearray.__iter__(self))

    def __repr__(self):
        return '[{0}]'.format(', '.join(repr(byte) for byte in self))

    def __str__(self):
        return ' '.join(str(byte) for byte in self)


class HexByte(int):
    width = 1

    def __new__(cls, x=0):
        if isinstance(x, str):
            self = int.__new__(cls, x, base=16)
        else:
            self = int.__new__(cls, x)
        maximum = 2 ** (self.width * 8)
        if 0 <= self < maximum:
            return self
        raise ValueError('Out of range')

    def chr(self):
        return chr(self) if 0x20 <= self <= 0x7e else '.'

    def hex(self, prefix=True):
        width = 2 * self.width
        if prefix:
            width += 2
        prefix = '#' if prefix else ''
        fmt = '{prefix}0{width}x'.format(prefix=prefix, width=width)
        return format(self, fmt)

    __hex__ = __repr__ = hex

    def __str__(self):
        return self.hex(prefix=False)


class HexWord(HexByte):
    width = 2

    def __new__(cls, x=0):
        if isinstance(x, Iterable) and not isinstance(x, str):
            h, l = x
            x = h << 8 | l
        self = HexByte.__new__(cls, x)
        return self

    def __iter__(self):
        return iter(map(HexByte, divmod(self, 0x100)))


class IPAddress(bytearray):

    def __init__(self, address):
        if isinstance(address, str):
            try:
                address = [int(o) for o in address.split('.')]
            except ValueError:
                pass
        if len(address) != 4:
            raise HDLMiracleIPAddressError('Cannot parse an IP Address')
        bytearray.__init__(self, address)

    def __repr__(self):
        return repr(str(self))

    def __str__(self):
        return '.'.join([str(o) for o in self])
