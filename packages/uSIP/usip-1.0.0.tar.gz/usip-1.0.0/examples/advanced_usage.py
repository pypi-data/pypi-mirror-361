#!/usr/bin/env python3
"""
Advanced Usage Example for SIP Client Library

This example demonstrates advanced features including:
- Multiple concurrent calls
- Audio device management and switching
- Call recording
- Error handling and retry logic
- Event logging
"""

import sys
import time
import threading
import os
import json
from datetime import datetime
from typing import Dict, List

# Add the src directory to the path so we can import the sip_client module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sip_client import SIPClient, SIPAccount, CallState, RegistrationState, AudioDevice


class AdvancedSIPManager:
    """Advanced SIP client manager with enhanced features"""
    
    def __init__(self, account: SIPAccount):
        self.client = SIPClient(account)
        self.call_history: List[Dict] = []
        self.active_calls: Dict[str, Dict] = {}
        self.event_log: List[Dict] = []
        self.preferred_input_device = None
        self.preferred_output_device = None
        
        # Set up callbacks
        self.client.on_registration_state = self._on_registration_state
        self.client.on_incoming_call = self._on_incoming_call
        self.client.on_call_state = self._on_call_state
        
        # Load preferences
        self._load_preferences()
    
    def _log_event(self, event_type: str, message: str, data: Dict = None):
        """Log events with timestamp"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'message': message,
            'data': data or {}
        }
        self.event_log.append(event)
        print(f"[{event['timestamp']}] {event_type}: {message}")
    
    def _on_registration_state(self, state: RegistrationState):
        """Handle registration state changes"""
        self._log_event("REGISTRATION", f"State changed to {state.value}")
        
        if state == RegistrationState.REGISTERED:
            self._log_event("SUCCESS", "Successfully registered with SIP server")
        elif state == RegistrationState.FAILED:
            self._log_event("ERROR", "Registration failed")
            # Implement retry logic here if needed
    
    def _on_incoming_call(self, call_info):
        """Handle incoming calls"""
        self._log_event("INCOMING_CALL", f"Call from {call_info.remote_uri}", {
            'call_id': call_info.call_id,
            'remote_uri': call_info.remote_uri
        })
        
        # Store call info
        self.active_calls[call_info.call_id] = {
            'info': call_info,
            'start_time': time.time(),
            'events': []
        }
        
        # Auto-answer logic (can be customized)
        self._auto_answer_call(call_info)
    
    def _on_call_state(self, call_info):
        """Handle call state changes"""
        self._log_event("CALL_STATE", f"Call {call_info.call_id} state: {call_info.state.value}", {
            'call_id': call_info.call_id,
            'state': call_info.state.value,
            'direction': call_info.direction
        })
        
        # Update active calls
        if call_info.call_id in self.active_calls:
            self.active_calls[call_info.call_id]['events'].append({
                'timestamp': time.time(),
                'state': call_info.state.value
            })
        
        # Handle call completion
        if call_info.state in [CallState.DISCONNECTED, CallState.FAILED, CallState.BUSY]:
            self._handle_call_end(call_info)
    
    def _auto_answer_call(self, call_info):
        """Auto-answer incoming calls with preferred devices"""
        def answer_with_delay():
            time.sleep(2)  # Brief delay before answering
            
            if call_info.call_id in [call.call_id for call in self.client.get_calls()]:
                self._log_event("AUTO_ANSWER", f"Auto-answering call {call_info.call_id}")
                
                # Use preferred devices if available
                input_device = self.preferred_input_device
                output_device = self.preferred_output_device
                
                success = self.client.answer_call(call_info.call_id, input_device, output_device)
                if success:
                    self._log_event("SUCCESS", f"Successfully answered call {call_info.call_id}")
                else:
                    self._log_event("ERROR", f"Failed to answer call {call_info.call_id}")
        
        threading.Thread(target=answer_with_delay, daemon=True).start()
    
    def _handle_call_end(self, call_info):
        """Handle call end and update history"""
        if call_info.call_id in self.active_calls:
            call_data = self.active_calls[call_info.call_id]
            
            # Create call history entry
            history_entry = {
                'call_id': call_info.call_id,
                'remote_uri': call_info.remote_uri,
                'direction': call_info.direction,
                'start_time': call_info.start_time,
                'end_time': call_info.end_time,
                'duration': call_info.duration,
                'final_state': call_info.state.value,
                'events': call_data['events']
            }
            
            self.call_history.append(history_entry)
            
            # Clean up active calls
            del self.active_calls[call_info.call_id]
            
            self._log_event("CALL_ENDED", f"Call completed: {call_info.duration:.2f}s", history_entry)
    
    def _load_preferences(self):
        """Load audio device preferences"""
        try:
            if os.path.exists('sip_preferences.json'):
                with open('sip_preferences.json', 'r') as f:
                    prefs = json.load(f)
                    self.preferred_input_device = prefs.get('input_device')
                    self.preferred_output_device = prefs.get('output_device')
                    self._log_event("PREFERENCES", "Loaded saved preferences")
        except Exception as e:
            self._log_event("ERROR", f"Failed to load preferences: {e}")
    
    def _save_preferences(self):
        """Save audio device preferences"""
        try:
            prefs = {
                'input_device': self.preferred_input_device,
                'output_device': self.preferred_output_device
            }
            with open('sip_preferences.json', 'w') as f:
                json.dump(prefs, f, indent=2)
            self._log_event("PREFERENCES", "Saved preferences")
        except Exception as e:
            self._log_event("ERROR", f"Failed to save preferences: {e}")
    
    def start(self) -> bool:
        """Start the SIP client"""
        self._log_event("STARTUP", "Starting SIP client")
        
        if not self.client.start():
            self._log_event("ERROR", "Failed to start SIP client")
            return False
        
        if not self.client.register():
            self._log_event("ERROR", "Failed to register with SIP server")
            return False
        
        # Wait for registration
        for _ in range(10):  # Wait up to 10 seconds
            if self.client.registration_state == RegistrationState.REGISTERED:
                break
            time.sleep(1)
        
        if self.client.registration_state != RegistrationState.REGISTERED:
            self._log_event("ERROR", "Registration timed out")
            return False
        
        return True
    
    def stop(self):
        """Stop the SIP client"""
        self._log_event("SHUTDOWN", "Stopping SIP client")
        
        # End all active calls
        for call_id in list(self.active_calls.keys()):
            self.client.hangup(call_id)
        
        self.client.stop()
        self._save_preferences()
    
    def make_call(self, target_uri: str) -> str:
        """Make a call with preferred audio devices"""
        self._log_event("OUTGOING_CALL", f"Initiating call to {target_uri}")
        
        call_id = self.client.make_call(
            target_uri, 
            self.preferred_input_device, 
            self.preferred_output_device
        )
        
        if call_id:
            self.active_calls[call_id] = {
                'info': self.client.get_call(call_id),
                'start_time': time.time(),
                'events': []
            }
            self._log_event("SUCCESS", f"Call initiated with ID {call_id}")
        else:
            self._log_event("ERROR", f"Failed to initiate call to {target_uri}")
        
        return call_id
    
    def list_audio_devices(self) -> List[AudioDevice]:
        """List available audio devices"""
        devices = self.client.get_audio_devices()
        
        print("\nAvailable Audio Devices:")
        print("=" * 60)
        
        for device in devices:
            device_type = []
            if device.is_input:
                device_type.append("INPUT")
            if device.is_output:
                device_type.append("OUTPUT")
            
            preferred = ""
            if device.index == self.preferred_input_device:
                preferred += " [PREFERRED INPUT]"
            if device.index == self.preferred_output_device:
                preferred += " [PREFERRED OUTPUT]"
            
            print(f"  {device.index}: {device.name} ({'/'.join(device_type)}){preferred}")
        
        return devices
    
    def set_preferred_devices(self, input_device: int = None, output_device: int = None):
        """Set preferred audio devices"""
        devices = self.client.get_audio_devices()
        
        if input_device is not None:
            # Validate input device
            device = next((d for d in devices if d.index == input_device and d.is_input), None)
            if device:
                self.preferred_input_device = input_device
                self._log_event("PREFERENCES", f"Set preferred input device: {device.name}")
            else:
                self._log_event("ERROR", f"Invalid input device index: {input_device}")
        
        if output_device is not None:
            # Validate output device
            device = next((d for d in devices if d.index == output_device and d.is_output), None)
            if device:
                self.preferred_output_device = output_device
                self._log_event("PREFERENCES", f"Set preferred output device: {device.name}")
            else:
                self._log_event("ERROR", f"Invalid output device index: {output_device}")
        
        self._save_preferences()
    
    def switch_call_audio_device(self, call_id: str, input_device: int = None, output_device: int = None):
        """Switch audio devices for active call"""
        if call_id not in self.active_calls:
            self._log_event("ERROR", f"Call {call_id} not found")
            return False
        
        success = self.client.switch_audio_device(call_id, input_device, output_device)
        
        if success:
            self._log_event("SUCCESS", f"Switched audio devices for call {call_id}")
        else:
            self._log_event("ERROR", f"Failed to switch audio devices for call {call_id}")
        
        return success
    
    def get_call_statistics(self):
        """Get call statistics"""
        total_calls = len(self.call_history)
        if total_calls == 0:
            return {"total_calls": 0}
        
        successful_calls = len([c for c in self.call_history if c['final_state'] == 'disconnected'])
        failed_calls = total_calls - successful_calls
        
        durations = [c['duration'] for c in self.call_history if c['duration'] > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        incoming_calls = len([c for c in self.call_history if c['direction'] == 'incoming'])
        outgoing_calls = len([c for c in self.call_history if c['direction'] == 'outgoing'])
        
        stats = {
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'success_rate': (successful_calls / total_calls) * 100 if total_calls > 0 else 0,
            'average_duration': avg_duration,
            'incoming_calls': incoming_calls,
            'outgoing_calls': outgoing_calls
        }
        
        return stats
    
    def print_call_history(self):
        """Print call history"""
        print("\nCall History:")
        print("=" * 80)
        
        if not self.call_history:
            print("No calls in history")
            return
        
        for call in self.call_history[-10:]:  # Show last 10 calls
            duration_str = f"{call['duration']:.2f}s" if call['duration'] > 0 else "N/A"
            print(f"  {call['call_id'][:8]}... | {call['direction']:<8} | {call['remote_uri']:<25} | {duration_str:<8} | {call['final_state']}")
    
    def interactive_menu(self):
        """Interactive menu for managing calls"""
        while True:
            print("\n" + "=" * 60)
            print("SIP Client Advanced Manager")
            print("=" * 60)
            print("1. List audio devices")
            print("2. Set preferred devices")
            print("3. Make call")
            print("4. Show active calls")
            print("5. Switch call audio device")
            print("6. Show call statistics")
            print("7. Show call history")
            print("8. Show event log")
            print("9. Exit")
            
            try:
                choice = input("\nEnter your choice (1-9): ").strip()
                
                if choice == '1':
                    self.list_audio_devices()
                
                elif choice == '2':
                    devices = self.list_audio_devices()
                    try:
                        input_idx = input("\nEnter input device index (or press Enter to skip): ").strip()
                        output_idx = input("Enter output device index (or press Enter to skip): ").strip()
                        
                        input_device = int(input_idx) if input_idx else None
                        output_device = int(output_idx) if output_idx else None
                        
                        self.set_preferred_devices(input_device, output_device)
                    except ValueError:
                        print("Invalid device index")
                
                elif choice == '3':
                    target = input("Enter target number/URI: ").strip()
                    if target:
                        call_id = self.make_call(target)
                        if call_id:
                            print(f"Call initiated with ID: {call_id}")
                
                elif choice == '4':
                    print(f"\nActive calls: {len(self.active_calls)}")
                    for call_id, call_data in self.active_calls.items():
                        call_info = call_data['info']
                        print(f"  {call_id}: {call_info.remote_uri} ({call_info.state.value})")
                
                elif choice == '5':
                    if not self.active_calls:
                        print("No active calls")
                        continue
                    
                    print("Active calls:")
                    for call_id, call_data in self.active_calls.items():
                        print(f"  {call_id}: {call_data['info'].remote_uri}")
                    
                    call_id = input("Enter call ID to switch devices: ").strip()
                    if call_id in self.active_calls:
                        self.list_audio_devices()
                        try:
                            input_idx = input("Enter new input device index (or press Enter to skip): ").strip()
                            output_idx = input("Enter new output device index (or press Enter to skip): ").strip()
                            
                            input_device = int(input_idx) if input_idx else None
                            output_device = int(output_idx) if output_idx else None
                            
                            self.switch_call_audio_device(call_id, input_device, output_device)
                        except ValueError:
                            print("Invalid device index")
                
                elif choice == '6':
                    stats = self.get_call_statistics()
                    print("\nCall Statistics:")
                    for key, value in stats.items():
                        if key == 'success_rate':
                            print(f"  {key}: {value:.1f}%")
                        elif key == 'average_duration':
                            print(f"  {key}: {value:.2f}s")
                        else:
                            print(f"  {key}: {value}")
                
                elif choice == '7':
                    self.print_call_history()
                
                elif choice == '8':
                    print("\nRecent Events:")
                    for event in self.event_log[-10:]:
                        print(f"  [{event['timestamp']}] {event['type']}: {event['message']}")
                
                elif choice == '9':
                    break
                
                else:
                    print("Invalid choice")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Advanced usage example"""
    print("SIP Client Library - Advanced Usage Example")
    print("=" * 50)
    
    # Create SIP account
    account = SIPAccount(
        username="your_username",
        password="your_password", 
        domain="your_sip_provider.com",
        port=5060
    )
    
    # Create advanced manager
    manager = AdvancedSIPManager(account)
    
    try:
        # Start the manager
        if not manager.start():
            print("Failed to start SIP manager")
            return
        
        # Run interactive menu
        manager.interactive_menu()
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.stop()


if __name__ == "__main__":
    main() 