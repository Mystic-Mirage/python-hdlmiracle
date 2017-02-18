class HDLMiracleException(Exception):
    pass


class HDLMiracleBusException(HDLMiracleException):
    pass


class HDLMiracleIPAddressException(HDLMiracleException):
    pass


class HDLMiracleIPBusException(HDLMiracleBusException):
    pass


class HDLMiraclePacketException(HDLMiracleException):
    pass
