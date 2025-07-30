"""
Audio Manager - RTP audio streaming and management
"""

import socket
import struct
import select
import threading
import time
import logging
from typing import Optional, Tuple, Callable, List

from .devices import AudioDevice, AudioDeviceManager

try:
    import pyaudio
except ImportError:
    pyaudio = None

logger = logging.getLogger(__name__)


class AudioManager:
    """Audio manager for RTP streaming"""
    
    def __init__(self):
        if not pyaudio:
            raise ImportError("pyaudio is required for audio functionality")
        
        self.device_manager = AudioDeviceManager()
        self.input_stream = None
        self.output_stream = None
        self.rtp_socket = None
        self.audio_thread = None
        self.is_streaming = False
        self.current_input_device = None
        self.current_output_device = None
        self.remote_rtp_address = None
        
        # Audio parameters
        self.sample_rate = 8000
        self.channels = 1
        self.format = pyaudio.paInt16
        self.chunk_size = 160  # 20ms at 8kHz
        self.rtp_sequence = 0
        self.rtp_timestamp = 0
        
        # Callbacks
        self.on_audio_error: Optional[Callable[[str], None]] = None
    
    def get_audio_devices(self) -> List[AudioDevice]:
        """Get list of available audio devices"""
        return self.device_manager.get_devices()
    
    def get_default_input_device(self) -> Optional[AudioDevice]:
        """Get default input device"""
        return self.device_manager.get_default_input_device()
    
    def get_default_output_device(self) -> Optional[AudioDevice]:
        """Get default output device"""
        return self.device_manager.get_default_output_device()
    
    def start_audio_stream(self, input_device: int, output_device: int, 
                          rtp_port: int, remote_address: Optional[Tuple[str, int]] = None):
        """Start audio streaming with RTP"""
        try:
            # Validate devices
            if not self.device_manager.validate_device(input_device, for_input=True):
                raise ValueError(f"Invalid input device: {input_device}")
            if not self.device_manager.validate_device(output_device, for_input=False):
                raise ValueError(f"Invalid output device: {output_device}")
            
            # Create RTP socket
            self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.rtp_socket.bind(('0.0.0.0', rtp_port))
            self.rtp_socket.settimeout(0.1)
            
            self.remote_rtp_address = remote_address
            self.current_input_device = input_device
            self.current_output_device = output_device
            
            # Open audio streams
            self.input_stream = pyaudio.PyAudio().open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=input_device,
                frames_per_buffer=self.chunk_size
            )
            
            self.output_stream = pyaudio.PyAudio().open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=output_device,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_streaming = True
            self.rtp_sequence = 0
            self.rtp_timestamp = 0
            
            # Start audio processing thread
            self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
            self.audio_thread.start()
            
            logger.info(f"Audio streaming started on port {rtp_port}")
            
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            if self.on_audio_error:
                self.on_audio_error(str(e))
            self.stop_audio_stream()
            raise
    
    def set_remote_rtp_address(self, address: Tuple[str, int]):
        """Set remote RTP address for sending audio"""
        self.remote_rtp_address = address
        logger.info(f"Remote RTP address set to {address}")
    
    def stop_audio_stream(self):
        """Stop audio streaming"""
        self.is_streaming = False
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
        
        if self.rtp_socket:
            self.rtp_socket.close()
            self.rtp_socket = None
        
        logger.info("Audio streaming stopped")
    
    def switch_input_device(self, device_index: int) -> bool:
        """Switch input device during active call"""
        try:
            if not self.device_manager.validate_device(device_index, for_input=True):
                logger.error(f"Invalid input device: {device_index}")
                return False
            
            if self.input_stream:
                self.input_stream.stop_stream()
                self.input_stream.close()
            
            self.input_stream = pyaudio.PyAudio().open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            self.current_input_device = device_index
            logger.info(f"Switched to input device {device_index}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch input device: {e}")
            if self.on_audio_error:
                self.on_audio_error(str(e))
            return False
    
    def switch_output_device(self, device_index: int) -> bool:
        """Switch output device during active call"""
        try:
            if not self.device_manager.validate_device(device_index, for_input=False):
                logger.error(f"Invalid output device: {device_index}")
                return False
            
            if self.output_stream:
                self.output_stream.stop_stream()
                self.output_stream.close()
            
            self.output_stream = pyaudio.PyAudio().open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            self.current_output_device = device_index
            logger.info(f"Switched to output device {device_index}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch output device: {e}")
            if self.on_audio_error:
                self.on_audio_error(str(e))
            return False
    
    def _audio_loop(self):
        """Main audio processing loop"""
        while self.is_streaming:
            try:
                # Read audio from microphone
                if self.input_stream:
                    try:
                        audio_data = self.input_stream.read(self.chunk_size, 
                                                          exception_on_overflow=False)
                        
                        # Create RTP packet
                        rtp_header = struct.pack('!BBHII',
                            0x80,  # Version=2, Padding=0, Extension=0, CC=0
                            0x00,  # Marker=0, Payload Type=0 (PCMU)
                            self.rtp_sequence,
                            self.rtp_timestamp,
                            0x12345678  # SSRC
                        )
                        
                        rtp_packet = rtp_header + audio_data
                        
                        # Send RTP packet to remote address
                        if self.remote_rtp_address:
                            self.rtp_socket.sendto(rtp_packet, self.remote_rtp_address)
                        
                        self.rtp_sequence = (self.rtp_sequence + 1) & 0xFFFF
                        self.rtp_timestamp += self.chunk_size
                        
                    except Exception as e:
                        if "Input overflowed" not in str(e):
                            logger.warning(f"Audio input error: {e}")
                
                # Receive and play audio
                if self.rtp_socket:
                    try:
                        ready = select.select([self.rtp_socket], [], [], 0.001)
                        if ready[0]:
                            data, addr = self.rtp_socket.recvfrom(1024)
                            if len(data) > 12:  # RTP header is 12 bytes
                                audio_payload = data[12:]
                                if self.output_stream:
                                    self.output_stream.write(audio_payload)
                    except socket.timeout:
                        pass
                    except Exception as e:
                        logger.warning(f"RTP receive error: {e}")
                
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Audio loop error: {e}")
                if self.on_audio_error:
                    self.on_audio_error(str(e))
                break
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_audio_stream()
        if self.device_manager:
            self.device_manager.cleanup() 