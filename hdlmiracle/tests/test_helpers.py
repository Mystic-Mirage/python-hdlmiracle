import threading
import unittest

from hdlmiracle.helpers import ReprMixin, spawn


class TestClass(ReprMixin):
    __module__ = 'testmodule'

    def dict(self):
        return {'key': 'value'}


class TestReprMixin(unittest.TestCase):

    def test_repr_mixin(self):
        test_class_instance = TestClass()
        test_class_repr = repr(test_class_instance)
        self.assertEqual(test_class_repr,
                         "testmodule.TestClass(key='value')")


class TestSpawn(unittest.TestCase):

    def test_spawn(self):
        thread = spawn(lambda a, b='default': 'result', 'arg1', b='kwarg2')
        self.assertTrue(isinstance(thread, threading.Thread))


if __name__ == '__main__':
    unittest.main()
