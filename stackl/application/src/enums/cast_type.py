from enum import Enum

class CastType(Enum):
    UNICAST = 'unicast'
    MULTICAST = 'multicast'
    ANYCAST = 'anycast'
    BROADCAST = 'broadcast'
