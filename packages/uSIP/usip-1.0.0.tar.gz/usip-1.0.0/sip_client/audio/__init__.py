"""
SIP Client Audio - Audio management and device handling
"""

from .manager import AudioManager
from .devices import AudioDevice

__all__ = [
    "AudioManager",
    "AudioDevice",
] 