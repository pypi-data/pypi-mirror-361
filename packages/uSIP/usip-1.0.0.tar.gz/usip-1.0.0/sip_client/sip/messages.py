"""
SIP Message Building and Parsing
"""

import re
from typing import Dict, Optional, Tuple
from ..utils.helpers import get_hostname, get_local_ip


class SIPMessageBuilder:
    """Builder for SIP messages"""
    
    @staticmethod
    def create_message(method: str, uri: str, headers: Dict[str, str], body: str = "") -> str:
        """Create a SIP message"""
        message = f"{method} {uri} SIP/2.0\r\n"
        
        for header, value in headers.items():
            message += f"{header}: {value}\r\n"
        
        message += f"Content-Length: {len(body)}\r\n"
        message += "\r\n"
        message += body
        
        return message
    
    @staticmethod
    def create_register_headers(username: str, domain: str, port: int, 
                               local_tag: str, branch: str, call_id: str, 
                               cseq: int, expires: int = 3600) -> Dict[str, str]:
        """Create headers for REGISTER request"""
        return {
            'Via': f"SIP/2.0/UDP {get_hostname()}:{port};branch={branch}",
            'From': f"<sip:{username}@{domain}>;tag={local_tag}",
            'To': f"<sip:{username}@{domain}>",
            'Call-ID': call_id,
            'CSeq': f"{cseq} REGISTER",
            'Contact': f"<sip:{username}@{get_hostname()}:{port}>",
            'Max-Forwards': '70',
            'User-Agent': 'Python SIP Client Library 1.0',
            'Expires': str(expires)
        }
    
    @staticmethod
    def create_invite_headers(username: str, domain: str, port: int, target_uri: str,
                             local_tag: str, branch: str, call_id: str, 
                             cseq: int) -> Dict[str, str]:
        """Create headers for INVITE request"""
        return {
            'Via': f"SIP/2.0/UDP {get_hostname()}:{port};branch={branch}",
            'From': f"<sip:{username}@{domain}>;tag={local_tag}",
            'To': f"<{target_uri}>",
            'Call-ID': call_id,
            'CSeq': f"{cseq} INVITE",
            'Contact': f"<sip:{username}@{get_hostname()}:{port}>",
            'Max-Forwards': '70',
            'User-Agent': 'Python SIP Client Library 1.0',
            'Content-Type': 'application/sdp'
        }
    
    @staticmethod
    def create_ack_headers(username: str, domain: str, port: int,
                          local_tag: str, remote_tag: str, branch: str, 
                          call_id: str, cseq: int) -> Dict[str, str]:
        """Create headers for ACK request"""
        return {
            'Via': f"SIP/2.0/UDP {get_hostname()}:{port};branch={branch}",
            'From': f"<sip:{username}@{domain}>;tag={local_tag}",
            'To': f"<sip:{username}@{domain}>;tag={remote_tag}",
            'Call-ID': call_id,
            'CSeq': f"{cseq} ACK",
            'Max-Forwards': '70',
            'User-Agent': 'Python SIP Client Library 1.0'
        }
    
    @staticmethod
    def create_bye_headers(username: str, domain: str, port: int,
                          local_tag: str, remote_tag: str, branch: str, 
                          call_id: str, cseq: int) -> Dict[str, str]:
        """Create headers for BYE request"""
        return {
            'Via': f"SIP/2.0/UDP {get_hostname()}:{port};branch={branch}",
            'From': f"<sip:{username}@{domain}>;tag={local_tag}",
            'To': f"<sip:{username}@{domain}>;tag={remote_tag}",
            'Call-ID': call_id,
            'CSeq': f"{cseq} BYE",
            'Max-Forwards': '70',
            'User-Agent': 'Python SIP Client Library 1.0'
        }
    
    @staticmethod
    def create_sdp_body(username: str, rtp_port: int) -> str:
        """Create SDP body for audio call"""
        local_ip = get_local_ip()
        return f"""v=0
o={username} 123456 123456 IN IP4 {local_ip}
s=Python SIP Client Library
c=IN IP4 {local_ip}
t=0 0
m=audio {rtp_port} RTP/AVP 0 8 18 101
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:18 G729/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-16
a=sendrecv
"""


class SIPMessageParser:
    """Parser for SIP messages"""
    
    @staticmethod
    def parse_headers(message: str) -> Dict[str, str]:
        """Parse SIP headers from message"""
        headers = {}
        lines = message.split('\r\n')
        
        for line in lines[1:]:  # Skip first line (request/response line)
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        return headers
    
    @staticmethod
    def extract_tag(header: str) -> Optional[str]:
        """Extract tag from From or To header"""
        if 'tag=' in header:
            return header.split('tag=')[1].split(';')[0].strip()
        return None
    
    @staticmethod
    def extract_contact_uri(header: str) -> Optional[str]:
        """Extract contact URI from Contact header"""
        if '<' in header and '>' in header:
            return header.split('<')[1].split('>')[0].strip()
        else:
            # Simple format without < >
            return header.split('Contact:')[1].strip().split(';')[0].strip()
    
    @staticmethod
    def extract_call_id(message: str) -> Optional[str]:
        """Extract Call-ID from SIP message"""
        headers = SIPMessageParser.parse_headers(message)
        return headers.get('Call-ID')
    
    @staticmethod
    def extract_cseq(message: str) -> Optional[Tuple[int, str]]:
        """Extract CSeq number and method from SIP message"""
        headers = SIPMessageParser.parse_headers(message)
        cseq_header = headers.get('CSeq')
        if cseq_header:
            parts = cseq_header.split(' ', 1)
            if len(parts) == 2:
                try:
                    return int(parts[0]), parts[1]
                except ValueError:
                    pass
        return None
    
    @staticmethod
    def extract_from_uri(message: str) -> Optional[str]:
        """Extract URI from From header"""
        headers = SIPMessageParser.parse_headers(message)
        from_header = headers.get('From')
        if from_header:
            if '<' in from_header and '>' in from_header:
                return from_header.split('<')[1].split('>')[0]
            else:
                return from_header.split(':')[1].split(';')[0]
        return None
    
    @staticmethod
    def extract_to_uri(message: str) -> Optional[str]:
        """Extract URI from To header"""
        headers = SIPMessageParser.parse_headers(message)
        to_header = headers.get('To')
        if to_header:
            if '<' in to_header and '>' in to_header:
                return to_header.split('<')[1].split('>')[0]
            else:
                return to_header.split(':')[1].split(';')[0]
        return None
    
    @staticmethod
    def get_response_code(message: str) -> Optional[int]:
        """Extract response code from SIP response"""
        lines = message.split('\r\n')
        if lines:
            first_line = lines[0]
            if first_line.startswith('SIP/2.0'):
                parts = first_line.split(' ')
                if len(parts) >= 2:
                    try:
                        return int(parts[1])
                    except ValueError:
                        pass
        return None
    
    @staticmethod
    def get_method(message: str) -> Optional[str]:
        """Extract method from SIP request"""
        lines = message.split('\r\n')
        if lines:
            first_line = lines[0]
            if not first_line.startswith('SIP/2.0'):
                parts = first_line.split(' ')
                if len(parts) >= 1:
                    return parts[0]
        return None
    
    @staticmethod
    def extract_sdp_body(message: str) -> Optional[str]:
        """Extract SDP body from SIP message"""
        if '\r\n\r\n' in message:
            return message.split('\r\n\r\n')[1]
        return None
    
    @staticmethod
    def parse_sdp_rtp_port(sdp_body: str) -> Optional[int]:
        """Parse RTP port from SDP body"""
        for line in sdp_body.split('\n'):
            if line.startswith('m=audio'):
                parts = line.split(' ')
                if len(parts) >= 2:
                    try:
                        return int(parts[1])
                    except ValueError:
                        pass
        return None 