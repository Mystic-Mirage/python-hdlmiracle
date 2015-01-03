from time import sleep

import hdlmiracle


class Searcher(hdlmiracle.Device):

    def __init__(self):
        hdlmiracle.Device.__init__(self)
        self.found = []

    def receive_func(self, packet):
        if packet.opcode == hdlmiracle.OC_SEARCH_R:
            device_identify = (packet.src_netid, packet.src_devid,
                               packet.src_devtype)
            if device_identify not in self.found:
                self.found.append(device_identify)
                devtype = hdlmiracle.devtype_details(packet.src_devtype)
                print (' {0.src_netid:-3d}   '
                       ' {0.src_devid:-3d}   '
                       ' {0.src_devtype:-5d}   '
                       '{1[0]:14s}  ({1[1]})'.format(packet, devtype))

    @hdlmiracle.sendmethod
    def search_request(self):
        return hdlmiracle.Packet(opcode=hdlmiracle.OC_SEARCH,
                                 netid=hdlmiracle.ALL_NETWORKS,
                                 devid=hdlmiracle.ALL_DEVICES)


def main():
    hdlmiracle.init(hdlmiracle.SMARTCLOUD)

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

    hdlmiracle.quit()


if __name__ == '__main__':
    main()
