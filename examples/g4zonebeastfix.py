from hdlmiracle.bus import IPBus
from hdlmiracle.datatypes import HexArray, HexByte
from hdlmiracle.devices import Emulator
from hdlmiracle.operationcodes import (
    CHANNEL_RESPONSE,
    CHANNELS_REPORT,
    CHANNELS_STATUS,
    CHANNELS_STATUS_RESPONSE,
)
from hdlmiracle.packet import SMARTCLOUD


class ZoneBeastFixer(Emulator):
    channels = None
    channels_num = None

    def catch(self, packet):
        if packet.opcode == CHANNELS_REPORT:
            bytes_num = divmod(packet.content[2], 8)
            bytes_num = bytes_num[0] + (1 if bytes_num[1] else 0)
            shift = 0
            bits = 0
            for byte in range(bytes_num):
                byte_value = packet.content[3 + byte]
                byte_value <<= shift
                bits |= byte_value
                shift += 8
            if self.channels_num is None:
                self.channels_num = packet.content[2]
            if self.channels is None:
                self.channels = [None] * self.channels_num
            mask = 1
            for channel in range(self.channels_num):
                if bits & mask:
                    if not self.channels[channel]:
                        self.channels[channel] = 100
                else:
                    self.channels[channel] = 0
                mask <<= 1
            print(self.channels)
        elif packet.opcode == CHANNEL_RESPONSE:
            channel = packet.content[0]
            value = packet.content[2]
            self.channels[channel-1] = value

    def receive(self, packet):
        if packet.opcode == CHANNELS_STATUS:
            if self.channels is None:
                return
            content = HexArray([HexByte(self.channels_num),
                                HexArray(self.channels)])
            self.send(target_address=packet.address, content=content)

    def send(self, target_address, content):
        packet = self.packet(
            operation_code=CHANNELS_STATUS_RESPONSE,
            target_address=target_address,
            content=content,
        )
        return packet


def main():
    ip_bus = IPBus(head=SMARTCLOUD)
    zb_fix = ZoneBeastFixer(subnet_id=1, device_id=28)
    ip_bus.attach(zb_fix)

    print('Smart-Bus ZoneBeast Fixer Started...')
    ip_bus.serve()
    print('Smart-Bus ZoneBeast Fixer Stopped...')


if __name__ == '__main__':
    main()
