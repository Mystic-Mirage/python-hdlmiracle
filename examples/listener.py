from os import linesep

from hdlmiracle.bus import IPBus
from hdlmiracle.devices import Monitor


class Listener(Monitor):
    lines = 24

    def receive(self, packet):
        lines = list(packet.content.step())
        lines_num = len(lines)
        self.lines += lines_num if lines else 1

        if self.lines > 22:
            print(
                'netid devid devtype opcode dstnet dstdev'
                '           hex              ascii'
            )
            self.lines = lines_num + 1

        lines_repr = [str(line).ljust(25) + line.ascii() for line in lines]
        content = (linesep + ' ' * 42).join(lines_repr)

        print(
            ' {packet.subnet_id:-3d}  '
            ' {packet.device_id:-3d}  '
            ' {packet.device_type:-5d}  '
            '{packet.operation_code:-#06x} '
            ' {packet.target_subnet_id:-3d}   '
            ' {packet.target_device_id:-3d}    '
            '{content}'.format(packet=packet, content=content)
        )


def main():
    ip_bus = IPBus(strict=False)
    listener = Listener()
    ip_bus.attach(listener)

    print('Smart-Bus Listener Started...')
    ip_bus.serve()
    print('Smart-Bus Listener Stopped...')


if __name__ == '__main__':
    main()
