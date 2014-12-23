from time import sleep

import smartbus


class Searcher(smartbus.Device):

    def __init__(self):
        smartbus.Device.__init__(self)
        self.found = []

    def receive_func(self, packet):
        if packet.opcode == smartbus.OC_SEARCH_R:
            device_identify = (packet.src_netid, packet.src_devid,
                               packet.src_devtype)
            if device_identify not in self.found:
                self.found.append(device_identify)
                devtype_details = smartbus.devtype_details(packet.src_devtype)
                print (' {0.src_netid:-3d}   '
                       ' {0.src_devid:-3d}   '
                       ' {0.src_devtype:-5d}   '
                       '{1[0]:14s}  ({1[1]})'.format(packet, devtype_details))

    @smartbus.sendmethod
    def search_request(self):
        return smartbus.Packet(opcode=smartbus.OC_SEARCH,
                               netid=smartbus.ALL_NETWORKS,
                               devid=smartbus.ALL_DEVICES)


def main():
    smartbus.init()

    searcher = Searcher()
    print 'netid  devid  devtype           device_info'

    try:
        while True:
            searcher.search_request()
            sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        raise

    smartbus.quit()


if __name__ == '__main__':
    main()
