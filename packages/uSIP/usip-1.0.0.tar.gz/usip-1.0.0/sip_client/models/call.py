"""
SIP Call Model - Call information and state tracking
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from .enums import CallState


@dataclass
class CallInfo:
    """Call information and state tracking"""
    call_id: str
    local_uri: str
    remote_uri: str
    state: CallState
    direction: str  # "incoming" or "outgoing"
    start_time: Optional[float] = None
    answer_time: Optional[float] = None
    end_time: Optional[float] = None
    
    # SIP-specific fields
    local_tag: Optional[str] = None
    remote_tag: Optional[str] = None
    branch: Optional[str] = None
    cseq: int = 1
    contact_uri: Optional[str] = None
    
    # Audio-specific fields
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    
    # Additional metadata
    metadata: dict = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Calculate call duration in seconds"""
        if self.answer_time and self.end_time:
            return self.end_time - self.answer_time
        return 0.0
    
    @property
    def is_active(self) -> bool:
        """Check if call is currently active"""
        return self.state in [CallState.CALLING, CallState.RINGING, CallState.CONNECTED]
    
    @property
    def is_incoming(self) -> bool:
        """Check if this is an incoming call"""
        return self.direction == "incoming"
    
    @property
    def is_outgoing(self) -> bool:
        """Check if this is an outgoing call"""
        return self.direction == "outgoing"
    
    def __str__(self) -> str:
        return f"Call {self.call_id}: {self.remote_uri} ({self.state.value})" 