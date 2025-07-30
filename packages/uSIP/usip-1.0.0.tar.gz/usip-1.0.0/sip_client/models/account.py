"""
SIP Account Model - Account configuration for SIP client
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SIPAccount:
    """SIP account configuration"""
    username: str
    password: str
    domain: str
    port: int = 5060
    display_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate account configuration"""
        if not self.username or not self.password or not self.domain:
            raise ValueError("Username, password, and domain are required")
        
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
    
    @property
    def uri(self) -> str:
        """Get the SIP URI for this account"""
        return f"sip:{self.username}@{self.domain}"
    
    def __str__(self) -> str:
        return f"{self.username}@{self.domain}:{self.port}" 