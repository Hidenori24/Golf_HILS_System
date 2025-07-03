#!/usr/bin/env python3
"""
Golf HILS System - Trajectory Analysis Example

This example demonstrates how to analyze pre-recorded swing data
and generate trajectory visualizations.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from sim.ball_flight_simulator import GolfBallSimulator
from disp.trajectory_display import TrajectoryVisualizer
from data.golf_data_store import GolfDataStore

def create_sample_swing_data():
    """Create sample swing data for demonstration"""
    
    class MockSwingData:
        def __init__(self, timestamp, ax, ay, az, gx, gy, gz):
            self.timestamp = timestamp
            self.accel_x = ax
            self.accel_y = ay
            self.accel_z = az
            self.gyro_x = gx
            self.gyro_y = gy
            self.gyro_z = gz
    
    # Simulate a golf swing with realistic acceleration and gyroscope data
    swing_data = []
    
    # Pre-swing (setup)
    for i in range(10):
        swing_data.append(MockSwingData(
            timestamp=i*10,
            ax=0.1, ay=0.1, az=9.8,  # At rest
            gx=2.0, gy=1.0, gz=0.5   # Minimal movement
        ))
    
    # Backswing
    for i in range(10, 30):
        t = (i - 10) / 20.0  # 0 to 1
        swing_data.append(MockSwingData(
            timestamp=i*10,
            ax=1.0 + t*2.0,          # Gradually increasing acceleration
            ay=0.5 + t*1.5,
            az=9.8 + t*2.0,
            gx=10.0 + t*40.0,        # Increasing rotation
            gy=15.0 + t*60.0,
            gz=5.0 + t*20.0
        ))
    
    # Downswing (peak acceleration)
    for i in range(30, 40):
        t = (i - 30) / 10.0  # 0 to 1
        swing_data.append(MockSwingData(
            timestamp=i*10,
            ax=3.0 + t*8.0,          # High acceleration
            ay=2.0 + t*6.0,
            az=11.8 + t*8.0,
            gx=50.0 + t*100.0,       # Very high rotation
            gy=75.0 + t*150.0,
            gz=25.0 + t*80.0
        ))
    
    # Impact and follow-through
    for i in range(40, 60):
        t = (i - 40) / 20.0  # 0 to 1
        swing_data.append(MockSwingData(
            timestamp=i*10,
            ax=11.0 - t*9.0,         # Decreasing acceleration
            ay=8.0 - t*6.0,
            az=19.8 - t*8.0,
            gx=150.0 - t*120.0,      # Decreasing rotation
            gy=225.0 - t*180.0,
            gz=105.0 - t*90.0
        ))
    
    return swing_data

def analyze_multiple_clubs():
    """Analyze the same swing with different clubs"""
    
    print("Golf HILS Trajectory Analysis Example")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create simulator and visualizer
    simulator = GolfBallSimulator()
    visualizer = TrajectoryVisualizer()
    
    # Create sample swing data
    swing_data = create_sample_swing_data()
    
    # Test different clubs
    clubs = ["Driver", "3-Iron", "7-Iron", "P-Wedge"]
    
    results = {}
    
    for club in clubs:
        print(f"\nAnalyzing swing with {club}...")
        
        # Run simulation
        simulation_result = simulator.simulate_complete_shot(swing_data, club)
        results[club] = simulation_result
        
        # Print results
        sim_results = simulation_result['results']
        launch_conditions = simulation_result['launch_conditions']
        
        print(f"  Carry Distance: {sim_results.get('carry_distance', 0):.1f} m")
        print(f"  Max Height: {sim_results.get('max_height', 0):.1f} m")
        print(f"  Flight Time: {sim_results.get('flight_time', 0):.1f} s")
        print(f"  Ball Speed: {launch_conditions.get('ball_speed', 0):.1f} m/s")
        print(f"  Launch Angle: {launch_conditions.get('launch_angle', 0):.1f}°")
        print(f"  Spin Rate: {launch_conditions.get('spin_rate', 0):.0f} rpm")
        
        # Create trajectory visualization
        trajectory_data = []
        for point in simulation_result.get('trajectory', []):
            trajectory_data.append({
                'x': point.x,
                'y': point.y,
                'time': point.time
            })
        
        if trajectory_data:
            fig = visualizer.create_trajectory_plot(trajectory_data, simulation_result)
            filename = f"trajectory_analysis_{club.lower().replace('-', '_')}.png"
            visualizer.save_plot(filename)
            print(f"  Trajectory saved as: {filename}")
    
    # Summary comparison
    print(f"\nClub Comparison Summary:")
    print("-" * 50)
    print(f"{'Club':<12} {'Distance':<10} {'Height':<10} {'Time':<8}")
    print("-" * 50)
    
    for club in clubs:
        sim_results = results[club]['results']
        print(f"{club:<12} {sim_results.get('carry_distance', 0):<10.1f} "
              f"{sim_results.get('max_height', 0):<10.1f} "
              f"{sim_results.get('flight_time', 0):<8.1f}")
    
    return results

def store_analysis_results(results):
    """Store analysis results in database"""
    
    print("\nStoring results in database...")
    
    # Create data store
    data_store = GolfDataStore("analysis_example.db")
    
    # Create session
    session_id = data_store.create_session(
        player_name="ExamplePlayer",
        location="Analysis Lab",
        weather_conditions="Indoor Simulation",
        notes="Trajectory analysis example"
    )
    
    # Store each club result
    for club_name, simulation_result in results.items():
        # Create mock swing data
        swing_dict = {
            'timestamp': 1234567890,
            'club': club_name,
            'player': 'ExamplePlayer',
            'device_id': 'Simulator',
            'accel_x': 5.0,
            'accel_y': 3.0,
            'accel_z': 15.0,
            'gyro_x': 100.0,
            'gyro_y': 150.0,
            'gyro_z': 75.0
        }
        
        # Store swing and results
        swing_id = data_store.store_swing_data(session_id, swing_dict)
        data_store.store_simulation_result(swing_id, simulation_result)
        
        # Update statistics
        carry_distance = simulation_result['results'].get('carry_distance', 0)
        data_store.update_player_statistics('ExamplePlayer', club_name, carry_distance)
    
    # Display stored statistics
    stats = data_store.get_player_statistics('ExamplePlayer')
    print("\nStored Player Statistics:")
    for stat in stats:
        print(f"  {stat['club_name']}: Avg {stat['avg_distance']:.1f}m, "
              f"Max {stat['max_distance']:.1f}m, Swings: {stat['total_swings']}")
    
    # Export to CSV
    export_dir = data_store.export_to_csv("analysis_export")
    print(f"\nData exported to: {export_dir}")
    
    data_store.close()

def main():
    """Main example function"""
    try:
        # Run analysis
        results = analyze_multiple_clubs()
        
        # Store results
        store_analysis_results(results)
        
        print("\nTrajectory analysis example complete!")
        print("Check the generated PNG files for trajectory visualizations.")
        
    except Exception as e:
        print(f"Error in trajectory analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())