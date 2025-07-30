"""
SIP Protocol - Core SIP protocol handling
"""

import socket
import select
import threading
import logging
from typing import Dict, Optional, Tuple, Callable, Any

from .messages import SIPMessageBuilder, SIPMessageParser
from .authentication import SIPAuthenticator
from ..models.account import SIPAccount
from ..models.call import CallInfo
from ..models.enums import CallState
from ..utils.helpers import generate_call_id, generate_tag, generate_branch

logger = logging.getLogger(__name__)


class SIPProtocol:
    """Core SIP protocol implementation"""
    
    def __init__(self, account: SIPAccount):
        self.account = account
        self.authenticator = SIPAuthenticator(account)
        self.socket = None
        self.message_thread = None
        self.listening = False
        self.cseq = 1
        
        # Callbacks
        self.on_message_received: Optional[Callable[[str, Tuple[str, int]], None]] = None
        self.on_response_received: Optional[Callable[[str, int], None]] = None
        self.on_request_received: Optional[Callable[[str, str], None]] = None
        
    def start(self) -> bool:
        """Start the SIP protocol handler"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(10)
            
            # Start message listener
            self.listening = True
            self.message_thread = threading.Thread(target=self._message_listener, daemon=True)
            self.message_thread.start()
            
            logger.info("SIP protocol started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SIP protocol: {e}")
            return False
    
    def stop(self):
        """Stop the SIP protocol handler"""
        self.listening = False
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        logger.info("SIP protocol stopped")
    
    def send_message(self, message: str, address: Optional[Tuple[str, int]] = None) -> bool:
        """Send SIP message"""
        try:
            if address is None:
                address = (self.account.domain, self.account.port)
            
            self.socket.sendto(message.encode(), address)
            logger.debug(f"Sent message to {address}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def send_register(self, expires: int = 3600) -> bool:
        """Send REGISTER request"""
        try:
            # Generate identifiers
            call_id = generate_call_id(self.account.domain)
            local_tag = generate_tag()
            branch = generate_branch()
            
            # Create REGISTER request
            uri = f"sip:{self.account.domain}"
            headers = SIPMessageBuilder.create_register_headers(
                self.account.username, self.account.domain, self.account.port,
                local_tag, branch, call_id, self.cseq, expires
            )
            
            message = SIPMessageBuilder.create_message('REGISTER', uri, headers)
            
            # Send message
            result = self.send_message(message)
            if result:
                self.cseq += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send REGISTER: {e}")
            return False
    
    def send_invite(self, target_uri: str, rtp_port: int = 10000) -> Optional[str]:
        """Send INVITE request"""
        try:
            # Generate identifiers
            call_id = generate_call_id(self.account.domain)
            local_tag = generate_tag()
            branch = generate_branch()
            
            # Create INVITE request
            headers = SIPMessageBuilder.create_invite_headers(
                self.account.username, self.account.domain, self.account.port,
                target_uri, local_tag, branch, call_id, self.cseq
            )
            
            # Create SDP body
            body = SIPMessageBuilder.create_sdp_body(self.account.username, rtp_port)
            
            message = SIPMessageBuilder.create_message('INVITE', target_uri, headers, body)
            
            # Send message
            result = self.send_message(message)
            if result:
                self.cseq += 1
                return call_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to send INVITE: {e}")
            return None
    
    def send_ack(self, call_info: CallInfo) -> bool:
        """Send ACK request"""
        try:
            # Use contact URI if available, otherwise use domain
            if call_info.contact_uri:
                uri = call_info.contact_uri
            else:
                uri = f"sip:{self.account.domain}"
            
            # Generate new branch for ACK
            branch = generate_branch()
            
            headers = SIPMessageBuilder.create_ack_headers(
                self.account.username, self.account.domain, self.account.port,
                call_info.local_tag, call_info.remote_tag, branch, 
                call_info.call_id, call_info.cseq
            )
            
            message = SIPMessageBuilder.create_message('ACK', uri, headers)
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send ACK: {e}")
            return False
    
    def send_bye(self, call_info: CallInfo) -> bool:
        """Send BYE request"""
        try:
            uri = f"sip:{self.account.domain}"
            call_info.cseq += 1
            
            headers = SIPMessageBuilder.create_bye_headers(
                self.account.username, self.account.domain, self.account.port,
                call_info.local_tag, call_info.remote_tag, generate_branch(),
                call_info.call_id, call_info.cseq
            )
            
            message = SIPMessageBuilder.create_message('BYE', uri, headers)
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send BYE: {e}")
            return False
    
    def send_response(self, response_code: int, response_text: str, 
                     request_message: str, additional_headers: Optional[Dict[str, str]] = None) -> bool:
        """Send SIP response"""
        try:
            # Parse original request
            headers = SIPMessageParser.parse_headers(request_message)
            
            # Create response headers
            response_headers = {
                'Via': headers.get('Via', ''),
                'From': headers.get('From', ''),
                'To': headers.get('To', ''),
                'Call-ID': headers.get('Call-ID', ''),
                'CSeq': headers.get('CSeq', ''),
                'User-Agent': 'Python SIP Client Library 1.0'
            }
            
            if additional_headers:
                response_headers.update(additional_headers)
            
            # Create response line
            response_line = f"SIP/2.0 {response_code} {response_text}"
            
            # Build response message
            message = f"{response_line}\r\n"
            for header, value in response_headers.items():
                message += f"{header}: {value}\r\n"
            message += "Content-Length: 0\r\n"
            message += "\r\n"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send response: {e}")
            return False
    
    def handle_auth_challenge(self, response: str, method: str, uri: str) -> bool:
        """Handle authentication challenge"""
        try:
            # Generate new identifiers
            call_id = generate_call_id(self.account.domain)
            local_tag = generate_tag()
            
            # Let authenticator handle the challenge
            auth_message = self.authenticator.handle_auth_challenge(
                response, method, uri, local_tag, call_id, self.cseq
            )
            
            if auth_message:
                result = self.send_message(auth_message)
                if result:
                    self.cseq += 1
                return result
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to handle auth challenge: {e}")
            return False
    
    def _message_listener(self):
        """Listen for incoming SIP messages"""
        while self.listening:
            try:
                if self.socket:
                    ready = select.select([self.socket], [], [], 1.0)
                    if ready[0]:
                        data, addr = self.socket.recvfrom(4096)
                        message = data.decode()
                        self._handle_incoming_message(message, addr)
            except Exception as e:
                if self.listening:
                    logger.error(f"Message listener error: {e}")
    
    def _handle_incoming_message(self, message: str, addr: Tuple[str, int]):
        """Handle incoming SIP message"""
        logger.debug(f"Received message from {addr}: {message}")
        
        # Notify callback
        if self.on_message_received:
            self.on_message_received(message, addr)
        
        # Parse message type
        lines = message.split('\r\n')
        if not lines:
            return
        
        first_line = lines[0]
        
        if first_line.startswith('SIP/2.0'):
            # Response
            response_code = SIPMessageParser.get_response_code(message)
            if response_code and self.on_response_received:
                self.on_response_received(message, response_code)
        else:
            # Request
            method = SIPMessageParser.get_method(message)
            if method and self.on_request_received:
                self.on_request_received(message, method)
    
    def extract_sip_info(self, message: str) -> Dict[str, Any]:
        """Extract SIP information from message"""
        headers = SIPMessageParser.parse_headers(message)
        
        info = {
            'call_id': headers.get('Call-ID'),
            'from_uri': SIPMessageParser.extract_from_uri(message),
            'to_uri': SIPMessageParser.extract_to_uri(message),
            'from_tag': None,
            'to_tag': None,
            'contact_uri': None,
            'cseq': SIPMessageParser.extract_cseq(message),
            'method': SIPMessageParser.get_method(message),
            'response_code': SIPMessageParser.get_response_code(message)
        }
        
        # Extract tags
        if 'From' in headers:
            info['from_tag'] = SIPMessageParser.extract_tag(headers['From'])
        if 'To' in headers:
            info['to_tag'] = SIPMessageParser.extract_tag(headers['To'])
        
        # Extract contact URI
        if 'Contact' in headers:
            info['contact_uri'] = SIPMessageParser.extract_contact_uri(headers['Contact'])
        
        return info 