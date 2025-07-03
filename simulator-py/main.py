#!/usr/bin/env python3
"""
Golf HILS System - Main Simulator Application

This is the main entry point for the Golf HILS simulation system running on Raspberry Pi.
It integrates all components: data reception, simulation, storage, and display.

Usage:
    python main.py [options]

Options:
    --port PORT         Serial port for sensor communication (default: /dev/ttyUSB0)
    --baud BAUD         Baud rate for serial communication (default: 115200)
    --display MODE      Display mode: live, headless, or both (default: live)
    --config CONFIG     Configuration file path (default: config/simulator_config.yaml)
    --log-level LEVEL   Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
"""

import argparse
import logging
import time
import threading
import signal
import sys
from typing import Dict, Any

# Import local modules
from comm.serial_data_listener import SerialDataListener, SwingData
from sim.ball_flight_simulator import GolfBallSimulator
from data.golf_data_store import GolfDataStore
from disp.trajectory_display import TrajectoryVisualizer, LiveDisplayManager

class GolfHILSSimulator:
    """Main Golf HILS simulator application"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Component initialization
        self.data_listener = None
        self.simulator = None
        self.data_store = None
        self.display_manager = None
        self.trajectory_visualizer = None
        
        # State management
        self.current_session_id = None
        self.swing_data_buffer = []
        self.is_running = True
        self.swing_in_progress = False
        
        # Threading
        self.display_thread = None
        self.data_thread = None
        
        self.logger.info("Golf HILS Simulator initialized")
    
    def initialize_components(self) -> bool:
        """Initialize all system components"""
        try:
            # Initialize data listener
            self.data_listener = SerialDataListener(
                port=self.config['serial']['port'],
                baud_rate=self.config['serial']['baud_rate']
            )
            self.data_listener.set_data_callback(self.handle_swing_data)
            
            # Initialize simulator
            self.simulator = GolfBallSimulator()
            
            # Initialize data store
            self.data_store = GolfDataStore(self.config['database']['path'])
            
            # Initialize display components
            if self.config['display']['mode'] in ['live', 'both']:
                self.display_manager = LiveDisplayManager(
                    screen_size=tuple(self.config['display']['screen_size'])
                )
            
            if self.config['display']['mode'] in ['headless', 'both']:
                self.trajectory_visualizer = TrajectoryVisualizer(
                    figure_size=tuple(self.config['display']['figure_size'])
                )
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False
    
    def start_session(self, player_name: str = "Unknown") -> bool:
        """Start a new practice session"""
        try:
            self.current_session_id = self.data_store.create_session(
                player_name=player_name,
                location=self.config.get('session', {}).get('location', 'Practice Range'),
                weather_conditions=self.config.get('session', {}).get('weather', 'Unknown'),
                notes=f"Automated session started at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            self.logger.info(f"Started session {self.current_session_id} for {player_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start session: {e}")
            return False
    
    def handle_swing_data(self, swing_data: SwingData):
        """Handle incoming swing data from sensor unit"""
        try:
            self.logger.info(f"Received swing data: {swing_data.player} - {swing_data.club}")
            
            # Add to buffer for swing analysis
            self.swing_data_buffer.append(swing_data)
            
            # Detect start of new swing (simple time-based detection)
            if not self.swing_in_progress:
                self.swing_in_progress = True
                self.swing_start_time = time.time()
                
                # Show swing detection on display
                if self.display_manager:
                    self.display_manager.display_swing_detected(
                        swing_data.player, swing_data.club
                    )
                
                # Start swing collection timer
                threading.Timer(2.0, self.process_swing).start()
            
            # Store individual swing data point
            if self.current_session_id:
                swing_dict = {
                    'timestamp': swing_data.timestamp,
                    'club': swing_data.club,
                    'player': swing_data.player,
                    'device_id': swing_data.device_id,
                    'accel_x': swing_data.accel_x,
                    'accel_y': swing_data.accel_y,
                    'accel_z': swing_data.accel_z,
                    'gyro_x': swing_data.gyro_x,
                    'gyro_y': swing_data.gyro_y,
                    'gyro_z': swing_data.gyro_z
                }
                self.data_store.store_swing_data(self.current_session_id, swing_dict)
            
        except Exception as e:
            self.logger.error(f"Error handling swing data: {e}")
    
    def process_swing(self):
        """Process complete swing data and run simulation"""
        try:
            if not self.swing_data_buffer:
                self.logger.warning("No swing data to process")
                return
            
            self.logger.info(f"Processing swing with {len(self.swing_data_buffer)} data points")
            
            # Get club name from latest data point
            club_name = self.swing_data_buffer[-1].club
            player_name = self.swing_data_buffer[-1].player
            
            # Run simulation
            simulation_results = self.simulator.simulate_complete_shot(
                self.swing_data_buffer, club_name
            )
            
            # Store simulation results
            if self.current_session_id and self.swing_data_buffer:
                # Find the swing ID for the first data point in this swing
                swing_dict = {
                    'timestamp': self.swing_data_buffer[0].timestamp,
                    'club': club_name,
                    'player': player_name,
                    'device_id': self.swing_data_buffer[0].device_id,
                    'accel_x': self.swing_data_buffer[0].accel_x,
                    'accel_y': self.swing_data_buffer[0].accel_y,
                    'accel_z': self.swing_data_buffer[0].accel_z,
                    'gyro_x': self.swing_data_buffer[0].gyro_x,
                    'gyro_y': self.swing_data_buffer[0].gyro_y,
                    'gyro_z': self.swing_data_buffer[0].gyro_z
                }
                swing_id = self.data_store.store_swing_data(self.current_session_id, swing_dict)
                self.data_store.store_simulation_result(swing_id, simulation_results)
                
                # Update player statistics
                carry_distance = simulation_results['results'].get('carry_distance', 0)
                self.data_store.update_player_statistics(player_name, club_name, carry_distance)
            
            # Display results
            self.display_results(simulation_results)
            
            # Log results
            results = simulation_results['results']
            self.logger.info(f"Simulation complete - Distance: {results.get('carry_distance', 0):.1f}m, "
                           f"Height: {results.get('max_height', 0):.1f}m")
            
            # Clear buffer and reset swing state
            self.swing_data_buffer = []
            self.swing_in_progress = False
            
            # Return to waiting state after displaying results
            if self.display_manager:
                threading.Timer(5.0, self.return_to_waiting).start()
            
        except Exception as e:
            self.logger.error(f"Error processing swing: {e}")
            self.swing_data_buffer = []
            self.swing_in_progress = False
    
    def display_results(self, simulation_results: Dict[str, Any]):
        """Display simulation results"""
        try:
            # Live display
            if self.display_manager:
                self.display_manager.display_simulation_results(simulation_results)
            
            # Generate and save trajectory plot
            if self.trajectory_visualizer:
                # Convert trajectory data for visualization
                trajectory_data = []
                for point in simulation_results.get('trajectory', []):
                    trajectory_data.append({
                        'x': point.x,
                        'y': point.y,
                        'time': point.time
                    })
                
                if trajectory_data:
                    fig = self.trajectory_visualizer.create_trajectory_plot(
                        trajectory_data, simulation_results
                    )
                    
                    # Save plot with timestamp
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"trajectories/trajectory_{timestamp}.png"
                    self.trajectory_visualizer.save_plot(filename)
            
        except Exception as e:
            self.logger.error(f"Error displaying results: {e}")
    
    def return_to_waiting(self):
        """Return display to waiting state"""
        if self.display_manager:
            self.display_manager.display_waiting_screen()
    
    def run_display_loop(self):
        """Run the display event loop in a separate thread"""
        if not self.display_manager:
            return
        
        self.display_manager.display_waiting_screen()
        
        while self.is_running:
            if not self.display_manager.handle_events():
                self.is_running = False
                break
            
            time.sleep(0.016)  # ~60 FPS
        
        self.display_manager.cleanup()
    
    def run_data_listener_loop(self):
        """Run the data listener in a separate thread"""
        if not self.data_listener:
            return
        
        if self.data_listener.connect():
            self.data_listener.listen_for_data()
    
    def start(self):
        """Start the main application"""
        try:
            self.logger.info("Starting Golf HILS Simulator")
            
            # Start session with default player
            if not self.start_session("DefaultPlayer"):
                self.logger.error("Failed to start session")
                return False
            
            # Start display thread
            if self.display_manager:
                self.display_thread = threading.Thread(target=self.run_display_loop, daemon=True)
                self.display_thread.start()
            
            # Start data listener thread
            self.data_thread = threading.Thread(target=self.run_data_listener_loop, daemon=True)
            self.data_thread.start()
            
            self.logger.info("All threads started, entering main loop")
            
            # Main loop
            while self.is_running:
                time.sleep(0.1)
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user")
            return True
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up resources")
        
        self.is_running = False
        
        if self.data_listener:
            self.data_listener.disconnect()
        
        if self.data_store:
            self.data_store.close()
        
        if self.display_manager:
            self.display_manager.cleanup()
        
        self.logger.info("Cleanup complete")

def load_default_config() -> Dict[str, Any]:
    """Load default configuration"""
    return {
        'serial': {
            'port': '/dev/ttyUSB0',
            'baud_rate': 115200
        },
        'display': {
            'mode': 'live',  # live, headless, both
            'screen_size': [1024, 768],
            'figure_size': [12, 8]
        },
        'database': {
            'path': 'golf_hils_data.db'
        },
        'session': {
            'location': 'Practice Range',
            'weather': 'Unknown'
        }
    }

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logging.getLogger(__name__).info("Received shutdown signal")
    sys.exit(0)

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Golf HILS Simulator')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate')
    parser.add_argument('--display', choices=['live', 'headless', 'both'], 
                       default='live', help='Display mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('golf_hils.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    config = load_default_config()
    config['serial']['port'] = args.port
    config['serial']['baud_rate'] = args.baud
    config['display']['mode'] = args.display
    
    # Create and run simulator
    simulator = GolfHILSSimulator(config)
    
    if not simulator.initialize_components():
        logger.error("Failed to initialize simulator")
        return 1
    
    logger.info("Starting Golf HILS Simulator")
    if simulator.start():
        logger.info("Simulator shutdown complete")
        return 0
    else:
        logger.error("Simulator failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())