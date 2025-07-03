"""
Golf HILS System - Ball Flight Simulator

This module implements the physics-based golf ball flight simulation engine.
It calculates ball trajectory, spin effects, air resistance, and landing position
based on initial swing data from the sensor unit.
"""

import math
import numpy as np
from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import logging

@dataclass
class LaunchConditions:
    """Initial launch conditions for golf ball"""
    ball_speed: float      # m/s
    launch_angle: float    # degrees
    spin_rate: float       # rpm
    carry_distance: float  # meters
    total_distance: float  # meters
    max_height: float      # meters
    flight_time: float     # seconds

@dataclass
class TrajectoryPoint:
    """Single point in ball trajectory"""
    time: float      # seconds
    x: float         # horizontal distance (m)
    y: float         # height (m)
    velocity_x: float # horizontal velocity (m/s)
    velocity_y: float # vertical velocity (m/s)

class GolfBallSimulator:
    """Physics-based golf ball flight simulator"""
    
    def __init__(self):
        # Physical constants
        self.GRAVITY = 9.81  # m/s^2
        self.AIR_DENSITY = 1.225  # kg/m^3 at sea level
        self.BALL_MASS = 0.0459  # kg (standard golf ball)
        self.BALL_RADIUS = 0.02135  # m (standard golf ball)
        self.BALL_AREA = math.pi * (self.BALL_RADIUS ** 2)
        
        # Aerodynamic coefficients
        self.DRAG_COEFFICIENT = 0.47  # Typical for golf ball
        self.MAGNUS_COEFFICIENT = 0.25  # For spin effects
        
        # Club specifications
        self.club_specs = {
            "Driver": {"loft": 10.5, "max_distance": 250},
            "3-Iron": {"loft": 21, "max_distance": 180},
            "5-Iron": {"loft": 27, "max_distance": 160},
            "7-Iron": {"loft": 34, "max_distance": 140},
            "9-Iron": {"loft": 42, "max_distance": 120},
            "P-Wedge": {"loft": 46, "max_distance": 100},
            "S-Wedge": {"loft": 56, "max_distance": 80},
            "Putter": {"loft": 4, "max_distance": 30}
        }
        
        self.logger = logging.getLogger(__name__)
    
    def analyze_swing_data(self, swing_data_points: List) -> Dict[str, float]:
        """Analyze swing data to extract swing characteristics"""
        if not swing_data_points:
            return {}
        
        # Calculate swing speed from gyroscope data
        max_angular_velocity = 0
        for point in swing_data_points:
            angular_vel = math.sqrt(point.gyro_x**2 + point.gyro_y**2 + point.gyro_z**2)
            max_angular_velocity = max(max_angular_velocity, angular_vel)
        
        # Calculate impact acceleration
        max_acceleration = 0
        for point in swing_data_points:
            accel_magnitude = math.sqrt(point.accel_x**2 + point.accel_y**2 + point.accel_z**2)
            max_acceleration = max(max_acceleration, accel_magnitude)
        
        # Convert to swing characteristics
        # These are simplified conversions - real implementation would use calibration data
        club_head_speed = max_angular_velocity * 0.5  # Simplified conversion
        impact_force = max_acceleration * 10  # Simplified conversion
        
        return {
            "club_head_speed": club_head_speed,
            "impact_force": impact_force,
            "max_angular_velocity": max_angular_velocity,
            "max_acceleration": max_acceleration
        }
    
    def calculate_initial_conditions(self, swing_analysis: Dict[str, float], 
                                   club_name: str) -> LaunchConditions:
        """Calculate initial ball launch conditions from swing analysis"""
        
        club_spec = self.club_specs.get(club_name, self.club_specs["7-Iron"])
        club_loft = club_spec["loft"]
        
        # Calculate ball speed (simplified model)
        club_head_speed = swing_analysis.get("club_head_speed", 30.0)  # m/s
        smash_factor = 1.4  # Typical for golf
        ball_speed = club_head_speed * smash_factor
        
        # Launch angle is influenced by club loft and swing characteristics
        launch_angle = club_loft * 0.7  # Simplified relationship
        
        # Spin rate calculation (simplified)
        spin_rate = club_head_speed * 100  # rpm, simplified
        
        # Create launch conditions
        return LaunchConditions(
            ball_speed=ball_speed,
            launch_angle=launch_angle,
            spin_rate=spin_rate,
            carry_distance=0,  # Will be calculated
            total_distance=0,  # Will be calculated
            max_height=0,      # Will be calculated
            flight_time=0      # Will be calculated
        )
    
    def simulate_trajectory(self, launch_conditions: LaunchConditions) -> List[TrajectoryPoint]:
        """Simulate complete ball trajectory with physics"""
        
        trajectory = []
        dt = 0.01  # 10ms time step
        
        # Initial conditions
        v0 = launch_conditions.ball_speed
        angle_rad = math.radians(launch_conditions.launch_angle)
        
        # Initial velocity components
        vx = v0 * math.cos(angle_rad)
        vy = v0 * math.sin(angle_rad)
        
        # Initial position
        x, y = 0.0, 0.0
        t = 0.0
        
        while y >= 0:  # Continue until ball hits ground
            # Calculate drag force
            velocity_magnitude = math.sqrt(vx**2 + vy**2)
            drag_force = 0.5 * self.AIR_DENSITY * self.DRAG_COEFFICIENT * self.BALL_AREA * velocity_magnitude**2
            
            # Drag acceleration components
            if velocity_magnitude > 0:
                drag_ax = -(drag_force / self.BALL_MASS) * (vx / velocity_magnitude)
                drag_ay = -(drag_force / self.BALL_MASS) * (vy / velocity_magnitude)
            else:
                drag_ax = drag_ay = 0
            
            # Magnus force (spin effect) - simplified
            magnus_force = self.MAGNUS_COEFFICIENT * launch_conditions.spin_rate * velocity_magnitude / 1000
            magnus_ay = magnus_force / self.BALL_MASS  # Upward lift for backspin
            
            # Total acceleration
            ax = drag_ax
            ay = drag_ay + magnus_ay - self.GRAVITY
            
            # Update velocity
            vx += ax * dt
            vy += ay * dt
            
            # Update position
            x += vx * dt
            y += vy * dt
            t += dt
            
            # Store trajectory point
            trajectory.append(TrajectoryPoint(
                time=t,
                x=x,
                y=y,
                velocity_x=vx,
                velocity_y=vy
            ))
        
        return trajectory
    
    def analyze_trajectory(self, trajectory: List[TrajectoryPoint]) -> Dict[str, float]:
        """Analyze trajectory to extract key metrics"""
        if not trajectory:
            return {}
        
        # Find maximum height and its time
        max_height = max(point.y for point in trajectory)
        max_height_time = next(point.time for point in trajectory if point.y == max_height)
        
        # Carry distance (where ball lands)
        carry_distance = trajectory[-1].x
        
        # Flight time
        flight_time = trajectory[-1].time
        
        # Landing angle
        landing_velocity = math.sqrt(trajectory[-1].velocity_x**2 + trajectory[-1].velocity_y**2)
        landing_angle = math.degrees(math.atan2(-trajectory[-1].velocity_y, trajectory[-1].velocity_x))
        
        return {
            "carry_distance": carry_distance,
            "max_height": max_height,
            "flight_time": flight_time,
            "landing_velocity": landing_velocity,
            "landing_angle": landing_angle,
            "apex_time": max_height_time
        }
    
    def simulate_complete_shot(self, swing_data_points: List, club_name: str) -> Dict[str, Any]:
        """Complete simulation from swing data to final result"""
        
        # Analyze swing data
        swing_analysis = self.analyze_swing_data(swing_data_points)
        
        # Calculate launch conditions
        launch_conditions = self.calculate_initial_conditions(swing_analysis, club_name)
        
        # Simulate trajectory
        trajectory = self.simulate_trajectory(launch_conditions)
        
        # Analyze results
        results = self.analyze_trajectory(trajectory)
        
        return {
            "swing_analysis": swing_analysis,
            "launch_conditions": launch_conditions.__dict__,
            "trajectory": trajectory,
            "results": results,
            "club_used": club_name
        }

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create simulator
    simulator = GolfBallSimulator()
    
    # Mock swing data for testing
    class MockSwingData:
        def __init__(self, ax, ay, az, gx, gy, gz):
            self.accel_x = ax
            self.accel_y = ay
            self.accel_z = az
            self.gyro_x = gx
            self.gyro_y = gy
            self.gyro_z = gz
    
    mock_data = [
        MockSwingData(2.0, 1.0, 9.8, 50, 100, 30),
        MockSwingData(5.0, 3.0, 12.0, 80, 150, 50),
        MockSwingData(8.0, 5.0, 15.0, 120, 200, 80),
    ]
    
    # Run simulation
    results = simulator.simulate_complete_shot(mock_data, "7-Iron")
    
    print("Simulation Results:")
    print(f"Carry Distance: {results['results']['carry_distance']:.1f} meters")
    print(f"Max Height: {results['results']['max_height']:.1f} meters")
    print(f"Flight Time: {results['results']['flight_time']:.1f} seconds")