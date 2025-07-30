"""
SIP Authentication - Handle digest authentication
"""

import hashlib
import logging
from typing import Dict, Optional, Tuple

from .messages import SIPMessageBuilder, SIPMessageParser
from ..models.account import SIPAccount
from ..utils.helpers import generate_branch

logger = logging.getLogger(__name__)


class SIPAuthenticator:
    """Handles SIP digest authentication"""
    
    def __init__(self, account: SIPAccount):
        self.account = account
    
    def parse_auth_challenge(self, response: str) -> Optional[Dict[str, str]]:
        """Parse authentication challenge from 401/407 response"""
        try:
            # Find authentication header
            auth_header = None
            for line in response.split('\r\n'):
                if line.startswith('WWW-Authenticate:') or line.startswith('Proxy-Authenticate:'):
                    auth_header = line
                    break
            
            if not auth_header:
                logger.error("No authentication header found")
                return None
            
            # Parse challenge parameters
            challenge = {}
            
            # Remove header name
            auth_data = auth_header.split(':', 1)[1].strip()
            
            # Remove 'Digest '
            if auth_data.startswith('Digest '):
                auth_data = auth_data[7:]
            
            # Parse parameters
            parts = auth_data.split(',')
            for part in parts:
                part = part.strip()
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    challenge[key] = value
            
            return challenge
            
        except Exception as e:
            logger.error(f"Failed to parse auth challenge: {e}")
            return None
    
    def create_auth_response(self, challenge: Dict[str, str], method: str, uri: str) -> str:
        """Create digest authentication response"""
        try:
            realm = challenge.get('realm', '')
            nonce = challenge.get('nonce', '')
            
            if not realm or not nonce:
                raise ValueError("Missing realm or nonce in challenge")
            
            # Calculate digest response
            ha1 = hashlib.md5(f"{self.account.username}:{realm}:{self.account.password}".encode()).hexdigest()
            ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
            response = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
            
            # Build authorization header
            auth_header = (
                f'Digest username="{self.account.username}", '
                f'realm="{realm}", '
                f'nonce="{nonce}", '
                f'uri="{uri}", '
                f'response="{response}"'
            )
            
            # Add optional parameters
            if 'opaque' in challenge:
                auth_header += f', opaque="{challenge["opaque"]}"'
            
            if 'algorithm' in challenge:
                auth_header += f', algorithm={challenge["algorithm"]}'
            
            return auth_header
            
        except Exception as e:
            logger.error(f"Failed to create auth response: {e}")
            raise
    
    def add_auth_header(self, headers: Dict[str, str], challenge: Dict[str, str], 
                       method: str, uri: str) -> Dict[str, str]:
        """Add Authorization header to existing headers"""
        auth_header = self.create_auth_response(challenge, method, uri)
        headers['Authorization'] = auth_header
        return headers
    
    def handle_auth_challenge(self, response: str, method: str, uri: str, 
                            local_tag: str, call_id: str, cseq: int) -> Optional[str]:
        """Handle authentication challenge and return authenticated request"""
        try:
            # Parse challenge
            challenge = self.parse_auth_challenge(response)
            if not challenge:
                return None
            
            # Create headers based on method
            if method == 'REGISTER':
                headers = SIPMessageBuilder.create_register_headers(
                    self.account.username, self.account.domain, self.account.port,
                    local_tag, generate_branch(), call_id, cseq
                )
            elif method == 'INVITE':
                headers = SIPMessageBuilder.create_invite_headers(
                    self.account.username, self.account.domain, self.account.port,
                    uri, local_tag, generate_branch(), call_id, cseq
                )
            else:
                logger.error(f"Unsupported method for authentication: {method}")
                return None
            
            # Add authentication
            headers = self.add_auth_header(headers, challenge, method, uri)
            
            # Create body for INVITE
            body = ""
            if method == 'INVITE':
                body = SIPMessageBuilder.create_sdp_body(self.account.username, 10000)
            
            # Build message
            message = SIPMessageBuilder.create_message(method, uri, headers, body)
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to handle auth challenge: {e}")
            return None
    
    def is_auth_required(self, response: str) -> bool:
        """Check if response requires authentication"""
        return "401 Unauthorized" in response or "407 Proxy Authentication Required" in response 