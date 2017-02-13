import unittest

import mock

from hdlmiracle.bus import Bus, DeviceSet
from hdlmiracle.devices import Driver
from hdlmiracle.packet import Packet


def spawn_stub(func, *args, **kwargs):
    func(*args, **kwargs)


class TestBusCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.device_10_100 = Driver(subnet_id=10, device_id=100)
        cls.device_20_100 = Driver(subnet_id=20, device_id=100)
        cls.device_20_150 = Driver(subnet_id=20, device_id=150)
        cls.device_30_100 = Driver(subnet_id=30, device_id=100)
        cls.device_30_150 = Driver(subnet_id=30, device_id=150)
        cls.device_30_200 = Driver(subnet_id=30, device_id=200)
        cls.segment_10_255 = [cls.device_10_100]
        cls.segment_20_255 = [cls.device_20_100, cls.device_20_150]
        cls.segment_30_255 = [cls.device_30_100, cls.device_30_150,
                              cls.device_30_200]
        cls.segment_255_100 = [cls.device_10_100, cls.device_20_100,
                               cls.device_30_100]
        cls.segment_255_150 = [cls.device_20_150, cls.device_30_150]
        cls.segment_255_200 = [cls.device_30_200]
        cls.segment_255_255 = [cls.device_10_100, cls.device_20_100,
                               cls.device_20_150, cls.device_30_100,
                               cls.device_30_150, cls.device_30_200]
        for device in cls.segment_255_255:
            device.catch = mock.Mock()
            device.receive = mock.Mock()


class TestBus(TestBusCase):

    def test_attach(self):
        bus = Bus()
        bus.attach(self.device_10_100)
        self.assertEqual(bus.devices, [self.device_10_100])

    def test_detach(self):
        bus = Bus(devices=[self.device_10_100, self.device_20_150])
        bus.detach(self.device_10_100)
        self.assertEqual(bus.devices, [self.device_20_150])

    def test_recv_catch(self):
        bus = Bus(devices=self.segment_255_255)
        bus.running = True

        packet_10_255 = Packet(address=(10, 255), target_address=(0, 0))
        packet_20_255 = Packet(address=(20, 255),  target_address=(0, 0))
        packet_30_255 = Packet(address=(30, 255), target_address=(0, 0))
        packet_255_100 = Packet(address=(255, 100), target_address=(0, 0))
        packet_255_150 = Packet(address=(255, 150), target_address=(0, 0))
        packet_255_200 = Packet(address=(255, 200), target_address=(0, 0))

        with mock.patch('hdlmiracle.bus.spawn', side_effect=spawn_stub):
            bus.recv(packet_10_255)
            bus.recv(packet_20_255)
            bus.recv(packet_30_255)
            bus.recv(packet_255_100)
            bus.recv(packet_255_150)
            bus.recv(packet_255_200)

        self.assertEqual(self.device_10_100.catch.call_count, 2)
        self.assertEqual(self.device_20_100.catch.call_count, 2)
        self.assertEqual(self.device_20_150.catch.call_count, 2)
        self.assertEqual(self.device_30_100.catch.call_count, 2)
        self.assertEqual(self.device_30_150.catch.call_count, 2)
        self.assertEqual(self.device_30_200.catch.call_count, 2)

    def test_recv_receive(self):
        bus = Bus(self.segment_255_255)
        bus.running = True

        packet_10_255 = Packet(target_subnet_id=10, target_device_id=255)
        packet_20_255 = Packet(target_subnet_id=20, target_device_id=255)
        packet_30_255 = Packet(target_subnet_id=30, target_device_id=255)
        packet_255_100 = Packet(target_subnet_id=255, target_device_id=100)
        packet_255_150 = Packet(target_subnet_id=255, target_device_id=150)
        packet_255_200 = Packet(target_subnet_id=255, target_device_id=200)
        packet_255_255 = Packet(target_subnet_id=255, target_device_id=255)

        with mock.patch('hdlmiracle.bus.spawn', side_effect=spawn_stub):
            bus.recv(packet_10_255)
            bus.recv(packet_20_255)
            bus.recv(packet_30_255)
            bus.recv(packet_255_100)
            bus.recv(packet_255_150)
            bus.recv(packet_255_200)
            bus.recv(packet_255_255)

        self.assertEqual(self.device_10_100.receive.call_count, 3)
        self.assertEqual(self.device_20_100.receive.call_count, 3)
        self.assertEqual(self.device_20_150.receive.call_count, 3)
        self.assertEqual(self.device_30_100.receive.call_count, 3)
        self.assertEqual(self.device_30_150.receive.call_count, 3)
        self.assertEqual(self.device_30_200.receive.call_count, 3)

    def test_send(self):
        bus = Bus([self.device_10_100])
        bus.send = mock.Mock()
        with mock.patch('hdlmiracle.bus.spawn', side_effect=spawn_stub):
            self.device_10_100.send()
        self.assertEqual(bus.send.called, True)


class TestDeviceSet(TestBusCase):

    def test_segments(self):
        device_set = DeviceSet()
        device_set.add(self.device_10_100)
        device_set.add(self.device_20_100)
        device_set.add(self.device_20_150)
        device_set.add(self.device_30_100)
        device_set.add(self.device_30_150)
        device_set.add(self.device_30_200)

        self.assertEqual(device_set[10, 255], set(self.segment_10_255))
        self.assertEqual(device_set[20, 255], set(self.segment_20_255))
        self.assertEqual(device_set[30, 255], set(self.segment_30_255))
        self.assertEqual(device_set[255, 100], set(self.segment_255_100))
        self.assertEqual(device_set[255, 150], set(self.segment_255_150))
        self.assertEqual(device_set[255, 200], set(self.segment_255_200))
        self.assertEqual(device_set[255, 255], set(self.segment_255_255))


if __name__ == '__main__':
    unittest.main()
