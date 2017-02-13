from hdlmiracle.bus import IPBus
from hdlmiracle.devices import Emulator, device_details
from hdlmiracle.operationcodes import SEARCH, SEARCH_RESPONSE
from hdlmiracle.packet import ALL_DEVICES, ALL_NETWORKS, SMARTCLOUD


class Searcher(Emulator):
    found = []

    def receive(self, packet):
        if packet.operation_code == SEARCH_RESPONSE:
            device = (packet.subnet_id, packet.device_id, packet.device_type)
            if device not in self.found:
                self.found.append(device)
                details = device_details(packet.device_type)
                print(
                    ' {packet.subnet_id:-3d}   '
                    ' {packet.device_id:-3d}   '
                    ' {packet.device_type:-5d}   '
                    '{details[0]:14s}  '
                    '({details[1]})'.format(packet=packet, details=details)
                )

    def heartbeat(self):
        return self.packet(
            operation_code=SEARCH,
            target_subnet_id=ALL_NETWORKS,
            target_device_id=ALL_DEVICES,
        )


def main():
    ip_bus = IPBus(head=SMARTCLOUD)
    searcher = Searcher()
    ip_bus.attach(searcher)

    print('netid  devid  devtype           device_info')
    ip_bus.serve()


if __name__ == '__main__':
    main()
