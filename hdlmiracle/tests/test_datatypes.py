import unittest

from hdlmiracle.datatypes import HexArray, HexByte, HexWord, IPAddress
from hdlmiracle.exceptions import HDLMiracleIPAddressError


class TestHexArray(unittest.TestCase):
    str = 'str'
    str_ha = [ord(s) for s in 'str']

    def test_from_str(self):
        ha = HexArray(self.str)
        self.assertEqual(ha, self.str_ha)

    def test_rerp(self):
        ha = HexArray(b'\x0a\x0b')
        self.assertEqual(repr(ha), '[0x0a, 0x0b]')

    def test_step(self):
        i = HexArray(6).step(4)
        self.assertEqual(len(next(i)), 4)
        self.assertEqual(len(next(i)), 2)
        with self.assertRaises(StopIteration):
            next(i)


class TestHexByte(unittest.TestCase):

    def test_default(self):
        b = HexByte()
        self.assertEqual(b, 0)

    def test_from_int(self):
        b = HexByte(1)
        self.assertEqual(b, 1)

    def test_from_str(self):
        b1 = HexByte('fe')
        b2 = HexByte('0xff')
        self.assertEqual((b1, b2), (0xfe, 0xff))

    def test_range(self):
        with self.assertRaises(ValueError):
            HexByte(-100)
        with self.assertRaises(ValueError):
            HexByte(500)

    def test_repr(self):
        b = HexByte(1)
        self.assertEqual(repr(b), '0x01')

    def test_str(self):
        b = HexByte(1)
        self.assertEqual(str(b), '01')


class TestHexWord(unittest.TestCase):

    def test_from_iterable(self):
        w = HexWord([0xfe, 0xff])
        self.assertEqual(w, 0xfeff)

    def test_from_str(self):
        w1 = HexWord('fffe')
        w2 = HexWord('0xffff')
        self.assertEqual((w1, w2), (0xfffe, 0xffff))

    def test_range(self):
        with self.assertRaises(ValueError):
            HexWord(-1000)
        with self.assertRaises(ValueError):
            HexWord(70000)

    def test_repr(self):
        w = HexWord(1)
        self.assertEqual(repr(w), '0x0001')

    def test_str(self):
        w = HexWord(1)
        self.assertEqual(str(w), '0001')

    def test_to_iterable(self):
        w = HexWord(0x0064)
        ba = bytearray()
        ba.extend(w)
        self.assertEqual(ba, b'\x00\x64')


class TestIPAddress(unittest.TestCase):
    str_ip = '10.11.12.13'
    bytes_ip = b'\x0a\x0b\x0c\x0d'

    def test_equal(self):
        ip = IPAddress(self.str_ip)
        self.assertEqual(ip, self.str_ip)

    def test_from_bytes(self):
        ip = IPAddress(self.bytes_ip)
        self.assertEqual(ip, IPAddress(self.str_ip))

    def test_repr(self):
        ip = IPAddress(self.str_ip)
        self.assertEqual(repr(ip), repr(self.str_ip))

    def test_str(self):
        ip = IPAddress(self.str_ip)
        self.assertEqual(str(ip), self.str_ip)

    def test_to_iterable(self):
        ip = IPAddress(self.str_ip)
        ba = bytearray()
        ba.extend(ip)
        self.assertEqual(ba, self.bytes_ip)

    def test_wrong_byte_length(self):
        with self.assertRaises(HDLMiracleIPAddressError):
            IPAddress(b'\x0a\x0b\x0c')
        with self.assertRaises(HDLMiracleIPAddressError):
            IPAddress(b'\x0a\x0b\x0c\x0d\x0e')

    def test_wrong_str_length(self):
        with self.assertRaises(HDLMiracleIPAddressError):
            IPAddress('1234')
        with self.assertRaises(HDLMiracleIPAddressError):
            IPAddress('10.11.12')
        with self.assertRaises(HDLMiracleIPAddressError):
            IPAddress('10.11.12.13.14')


if __name__ == '__main__':
    unittest.main()
