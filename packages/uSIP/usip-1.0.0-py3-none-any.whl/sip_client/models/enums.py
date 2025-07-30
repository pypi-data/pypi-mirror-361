"""
SIP Client Enums - State enumerations for SIP client library
"""

from enum import Enum


class CallState(Enum):
    """Call state enumeration"""
    IDLE = "idle"
    CALLING = "calling"
    RINGING = "ringing"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    BUSY = "busy"
    FAILED = "failed"


class RegistrationState(Enum):
    """Registration state enumeration"""
    UNREGISTERED = "unregistered"
    REGISTERING = "registering"
    REGISTERED = "registered"
    FAILED = "failed" 