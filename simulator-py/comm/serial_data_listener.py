"""
Golf HILS System - Serial Communication Listener

This module handles receiving swing data from the M5StickC Plus2 sensor unit
via USB serial connection. It parses JSON packets and forwards them to the
simulation engine.
"""

import serial
import json
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SwingData:
    """Data structure for golf swing measurements"""
    timestamp: int
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    club: str
    player: str
    device_id: str

class SerialDataListener:
    """Handles serial communication with M5StickC Plus2 sensor unit"""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baud_rate: int = 115200):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = None
        self.is_connected = False
        self.data_callback = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Establish serial connection to sensor unit"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1,
                write_timeout=1
            )
            
            # Wait for connection to stabilize
            time.sleep(2)
            
            self.is_connected = True
            self.logger.info(f"Connected to sensor unit on {self.port}")
            return True
            
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            self.logger.info("Disconnected from sensor unit")
    
    def set_data_callback(self, callback):
        """Set callback function for received data"""
        self.data_callback = callback
    
    def parse_swing_data(self, json_str: str) -> Optional[SwingData]:
        """Parse JSON string into SwingData object"""
        try:
            data_dict = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['timestamp', 'accel_x', 'accel_y', 'accel_z',
                             'gyro_x', 'gyro_y', 'gyro_z', 'club', 'player']
            
            for field in required_fields:
                if field not in data_dict:
                    self.logger.warning(f"Missing field '{field}' in data packet")
                    return None
            
            return SwingData(
                timestamp=data_dict['timestamp'],
                accel_x=float(data_dict['accel_x']),
                accel_y=float(data_dict['accel_y']),
                accel_z=float(data_dict['accel_z']),
                gyro_x=float(data_dict['gyro_x']),
                gyro_y=float(data_dict['gyro_y']),
                gyro_z=float(data_dict['gyro_z']),
                club=str(data_dict['club']),
                player=str(data_dict['player']),
                device_id=data_dict.get('device_id', 'unknown')
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse data: {e}")
            return None
    
    def listen_for_data(self) -> None:
        """Main listening loop for incoming data"""
        if not self.is_connected:
            self.logger.error("Not connected to sensor unit")
            return
        
        self.logger.info("Starting data listener...")
        
        try:
            while self.is_connected:
                if self.serial_connection.in_waiting > 0:
                    # Read line from serial
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line:
                        # Parse swing data
                        swing_data = self.parse_swing_data(line)
                        
                        if swing_data and self.data_callback:
                            # Forward data to callback
                            self.data_callback(swing_data)
                        
                        self.logger.debug(f"Received: {line}")
                
                # Small delay to prevent CPU overload
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            self.logger.info("Data listener stopped by user")
        except Exception as e:
            self.logger.error(f"Error in data listener: {e}")
        finally:
            self.disconnect()

    def send_acknowledgment(self, data_id: str) -> bool:
        """Send acknowledgment back to sensor unit"""
        if not self.is_connected:
            return False
        
        try:
            ack_message = json.dumps({"ack": data_id, "status": "received"})
            self.serial_connection.write(f"{ack_message}\n".encode())
            return True
        except Exception as e:
            self.logger.error(f"Failed to send acknowledgment: {e}")
            return False

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def data_received_callback(swing_data: SwingData):
        print(f"Received swing data from {swing_data.player} using {swing_data.club}")
        print(f"  Acceleration: ({swing_data.accel_x:.2f}, {swing_data.accel_y:.2f}, {swing_data.accel_z:.2f})")
        print(f"  Gyroscope: ({swing_data.gyro_x:.2f}, {swing_data.gyro_y:.2f}, {swing_data.gyro_z:.2f})")
        print(f"  Timestamp: {swing_data.timestamp}")
        print("-" * 50)
    
    # Create and start listener
    listener = SerialDataListener()
    listener.set_data_callback(data_received_callback)
    
    if listener.connect():
        listener.listen_for_data()