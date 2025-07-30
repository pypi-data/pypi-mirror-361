#!/usr/bin/env python3
"""
Basic Usage Example for SIP Client Library

This example demonstrates the basic functionality of the SIP client library
including registration, making calls, and handling events.
"""

import sys
import time
import threading
import os

# Add the src directory to the path so we can import the sip_client module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sip_client import SIPClient, SIPAccount, CallState, RegistrationState


def main():
    """Basic usage example"""
    print("SIP Client Library - Basic Usage Example")
    print("=" * 50)
    
    # Create SIP account
    # You can either pass the account details directly or use environment variables
    account = SIPAccount(
        username="your_username",
        password="your_password",
        domain="your_sip_provider.com",
        port=5060
    )
    
    # Alternatively, use environment variables by passing no parameters:
    # client = SIPClient()  # Will load from .env file or environment
    
    # Create SIP client
    client = SIPClient(account)
    
    # Set up event callbacks
    def on_registration_state(state: RegistrationState):
        print(f"Registration state: {state.value}")
        if state == RegistrationState.REGISTERED:
            print("✓ Successfully registered with SIP server")
        elif state == RegistrationState.FAILED:
            print("✗ Registration failed")
    
    def on_incoming_call(call_info):
        print(f"📞 Incoming call from {call_info.remote_uri}")
        print(f"   Call ID: {call_info.call_id}")
        
        # Auto-answer after 3 seconds (for demo purposes)
        def auto_answer():
            time.sleep(3)
            if call_info.call_id in [call.call_id for call in client.get_calls()]:
                print("   Auto-answering call...")
                client.answer_call(call_info.call_id)
        
        threading.Thread(target=auto_answer, daemon=True).start()
    
    def on_call_state(call_info):
        print(f"📞 Call {call_info.call_id} state: {call_info.state.value}")
        
        if call_info.state == CallState.CONNECTED:
            print("   ✓ Call connected!")
            if call_info.direction == "outgoing":
                print("   🎤 You can now talk (call will end automatically in 10 seconds)")
        elif call_info.state == CallState.DISCONNECTED:
            print(f"   ✗ Call ended. Duration: {call_info.duration:.2f} seconds")
        elif call_info.state == CallState.BUSY:
            print("   📵 Number is busy")
        elif call_info.state == CallState.FAILED:
            print("   ✗ Call failed")
    
    # Register callbacks
    client.on_registration_state = on_registration_state
    client.on_incoming_call = on_incoming_call
    client.on_call_state = on_call_state
    
    try:
        # 1. Start the client
        print("Starting SIP client...")
        if not client.start():
            print("Failed to start SIP client")
            return
        
        # 2. Register with SIP server
        print("Registering with SIP server...")
        if not client.register():
            print("Failed to register with SIP server")
            return
        
        # Wait for registration to complete
        time.sleep(2)
        
        if client.registration_state != RegistrationState.REGISTERED:
            print("Registration did not complete successfully")
            return
        
        # 3. List available audio devices
        print("\nAvailable audio devices:")
        devices = client.get_audio_devices()
        for device in devices:
            device_type = []
            if device.is_input:
                device_type.append("INPUT")
            if device.is_output:
                device_type.append("OUTPUT")
            print(f"  {device.index}: {device.name} ({'/'.join(device_type)})")
        
        # 4. Make an outgoing call
        print("\nMaking outgoing call...")
        target_number = "1234567890"  # Replace with actual number
        
        # Use default audio devices
        call_id = client.make_call(target_number)
        
        if call_id:
            print(f"Call initiated with ID: {call_id}")
            
            # Wait for call to establish
            time.sleep(3)
            
            # Check call status
            call_info = client.get_call(call_id)
            if call_info and call_info.state == CallState.CONNECTED:
                print("Call is connected!")
                
                # Let call run for 10 seconds
                time.sleep(10)
                
                # Hang up the call
                print("Hanging up call...")
                client.hangup(call_id)
            else:
                print("Call did not connect successfully")
        else:
            print("Failed to initiate call")
        
        # 5. Wait for incoming calls
        print("\nWaiting for incoming calls...")
        print("Press Ctrl+C to exit")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        client.stop()
        print("SIP client stopped")


if __name__ == "__main__":
    main() 