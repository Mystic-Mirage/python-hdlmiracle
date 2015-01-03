from time import sleep

import hdlmiracle


class ZoneBeastFixer(hdlmiracle.Device):

    def __init__(self, netid, devid):
        hdlmiracle.Device.__init__(self, netid=netid, devid=devid)
        self.channels = None
        self.channels_num = None

    @hdlmiracle.sendmethod
    def send(self, data, netid, devid):
        return hdlmiracle.Packet(hdlmiracle.OC_CHANNELS_STATUS_R, data, netid,
                                 devid, self.netid, self.devid, self.devtype)

    def receive_func(self, packet):
        if packet.opcode == hdlmiracle.OC_CHANNELS_STATUS:
            if self.channels is None:
                return
            data = bytearray([self.channels_num] + self.channels)
            self.send(data, packet.src_netid, packet.src_devid)

    def send_func(self, packet):
        if packet.opcode == hdlmiracle.OC_CHANNELS_REPORT:
            bytes_num = divmod(packet.data[2], 8)
            bytes_num = bytes_num[0] + (1 if bytes_num[1] else 0)
            shift = 0
            bits = 0
            for byte in range(bytes_num):
                byte_value = packet.data[3 + byte]
                byte_value <<= shift
                bits |= byte_value
                shift += 8
            if self.channels_num is None:
                self.channels_num = packet.data[2]
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
        if packet.opcode == hdlmiracle.OC_CHANNEL_CONTROL_R:
            channel = packet.data[0]
            value = packet.data[2]
            self.channels[channel - 1] = value


def main():
    hdlmiracle.init(hdlmiracle.SMARTCLOUD)
    ZoneBeastFixer(1, 28)
    print 'Smart-Bus ZoneBeastFixer Started...'

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
    except:
        raise

    hdlmiracle.quit()
    print 'Smart-Bus ZoneBeastFixer Stopped...'


if __name__ == '__main__':
    main()
