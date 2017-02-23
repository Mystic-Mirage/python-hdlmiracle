class HDLMiracleException(Exception):
    pass


class HDLMiracleBusException(HDLMiracleException):
    pass


class HDLMiracleIPAddressError(HDLMiracleException):
    pass


class HDLMiracleIPBusException(HDLMiracleBusException):
    pass


class HDLMiraclePacketError(HDLMiracleException):
    pass
