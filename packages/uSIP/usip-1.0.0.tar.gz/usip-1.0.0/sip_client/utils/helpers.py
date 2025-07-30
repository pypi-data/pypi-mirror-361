"""
Utility functions for SIP client
"""

import random
import socket


def generate_call_id(domain: str = None) -> str:
    """Generate a unique call ID"""
    if domain is None:
        domain = socket.gethostname()
    return f"{random.randint(100000, 999999)}@{domain}"


def generate_tag() -> str:
    """Generate a unique tag"""
    return f"{random.randint(100000, 999999)}"


def generate_branch() -> str:
    """Generate a unique branch identifier"""
    return f"z9hG4bK{random.randint(100000, 999999)}"


def get_local_ip() -> str:
    """Get local IP address"""
    return socket.gethostbyname(socket.gethostname())


def get_hostname() -> str:
    """Get local hostname"""
    return socket.gethostname() 