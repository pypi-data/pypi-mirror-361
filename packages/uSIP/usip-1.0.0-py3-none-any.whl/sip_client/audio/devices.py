"""
Audio Device Models - Audio device information and management
"""

from dataclasses import dataclass
from typing import List, Optional

try:
    import pyaudio
except ImportError:
    pyaudio = None


@dataclass
class AudioDevice:
    """Audio device information"""
    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: float
    
    @property
    def is_input(self) -> bool:
        """Check if device can be used for input"""
        return self.max_input_channels > 0
    
    @property
    def is_output(self) -> bool:
        """Check if device can be used for output"""
        return self.max_output_channels > 0
    
    def __str__(self) -> str:
        device_type = []
        if self.is_input:
            device_type.append("INPUT")
        if self.is_output:
            device_type.append("OUTPUT")
        return f"{self.name} ({'/'.join(device_type)})"


class AudioDeviceManager:
    """Audio device enumeration and management"""
    
    def __init__(self):
        if not pyaudio:
            raise ImportError("pyaudio is required for audio functionality")
        self.audio = pyaudio.PyAudio()
    
    def get_devices(self) -> List[AudioDevice]:
        """Get list of available audio devices"""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            devices.append(AudioDevice(
                index=i,
                name=info['name'],
                max_input_channels=info['maxInputChannels'],
                max_output_channels=info['maxOutputChannels'],
                default_sample_rate=info['defaultSampleRate']
            ))
        return devices
    
    def get_default_input_device(self) -> Optional[AudioDevice]:
        """Get default input device"""
        try:
            info = self.audio.get_default_input_device_info()
            return AudioDevice(
                index=info['index'],
                name=info['name'],
                max_input_channels=info['maxInputChannels'],
                max_output_channels=info['maxOutputChannels'],
                default_sample_rate=info['defaultSampleRate']
            )
        except Exception:
            return None
    
    def get_default_output_device(self) -> Optional[AudioDevice]:
        """Get default output device"""
        try:
            info = self.audio.get_default_output_device_info()
            return AudioDevice(
                index=info['index'],
                name=info['name'],
                max_input_channels=info['maxInputChannels'],
                max_output_channels=info['maxOutputChannels'],
                default_sample_rate=info['defaultSampleRate']
            )
        except Exception:
            return None
    
    def validate_device(self, device_index: int, for_input: bool = True) -> bool:
        """Validate if device can be used for input or output"""
        try:
            info = self.audio.get_device_info_by_index(device_index)
            if for_input:
                return info['maxInputChannels'] > 0
            else:
                return info['maxOutputChannels'] > 0
        except Exception:
            return False
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.audio:
            self.audio.terminate() 