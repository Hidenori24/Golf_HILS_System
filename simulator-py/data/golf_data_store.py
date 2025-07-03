"""
Golf HILS System - Data Storage and Management

This module handles persistent storage of swing data, simulation results,
and player statistics using SQLite database and CSV export functionality.
"""

import sqlite3
import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

class GolfDataStore:
    """Manages persistent storage of golf swing data and simulation results"""
    
    def __init__(self, db_path: str = "golf_hils_data.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_date TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    location TEXT,
                    weather_conditions TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create swings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS swings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    timestamp INTEGER NOT NULL,
                    club_name TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    device_id TEXT,
                    raw_data TEXT,  -- JSON string of swing data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            # Create simulation_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    swing_id INTEGER,
                    carry_distance REAL,
                    max_height REAL,
                    flight_time REAL,
                    ball_speed REAL,
                    launch_angle REAL,
                    spin_rate REAL,
                    landing_angle REAL,
                    trajectory_data TEXT,  -- JSON string of trajectory points
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (swing_id) REFERENCES swings (id)
                )
            """)
            
            # Create player_statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    club_name TEXT NOT NULL,
                    avg_distance REAL,
                    max_distance REAL,
                    avg_accuracy REAL,
                    total_swings INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(player_name, club_name)
                )
            """)
            
            self.connection.commit()
            self.logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def create_session(self, player_name: str, location: str = "", 
                      weather_conditions: str = "", notes: str = "") -> int:
        """Create a new practice session"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_date, player_name, location, weather_conditions, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), player_name, location, weather_conditions, notes))
            
            self.connection.commit()
            session_id = cursor.lastrowid
            self.logger.info(f"Created session {session_id} for {player_name}")
            return session_id
            
        except sqlite3.Error as e:
            self.logger.error(f"Error creating session: {e}")
            raise
    
    def store_swing_data(self, session_id: int, swing_data: Dict[str, Any]) -> int:
        """Store swing data from sensor"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO swings (session_id, timestamp, club_name, player_name, device_id, raw_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                swing_data.get('timestamp', int(datetime.now().timestamp() * 1000)),
                swing_data.get('club', 'Unknown'),
                swing_data.get('player', 'Unknown'),
                swing_data.get('device_id', 'Unknown'),
                json.dumps(swing_data)
            ))
            
            self.connection.commit()
            swing_id = cursor.lastrowid
            self.logger.debug(f"Stored swing data with ID {swing_id}")
            return swing_id
            
        except sqlite3.Error as e:
            self.logger.error(f"Error storing swing data: {e}")
            raise
    
    def store_simulation_result(self, swing_id: int, simulation_result: Dict[str, Any]) -> int:
        """Store simulation results"""
        try:
            cursor = self.connection.cursor()
            results = simulation_result.get('results', {})
            launch_conditions = simulation_result.get('launch_conditions', {})
            
            cursor.execute("""
                INSERT INTO simulation_results (
                    swing_id, carry_distance, max_height, flight_time, 
                    ball_speed, launch_angle, spin_rate, landing_angle, trajectory_data
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                swing_id,
                results.get('carry_distance', 0),
                results.get('max_height', 0),
                results.get('flight_time', 0),
                launch_conditions.get('ball_speed', 0),
                launch_conditions.get('launch_angle', 0),
                launch_conditions.get('spin_rate', 0),
                results.get('landing_angle', 0),
                json.dumps([
                    {
                        'time': p.time,
                        'x': p.x,
                        'y': p.y,
                        'vx': p.velocity_x,
                        'vy': p.velocity_y
                    } for p in simulation_result.get('trajectory', [])
                ])
            ))
            
            self.connection.commit()
            result_id = cursor.lastrowid
            self.logger.debug(f"Stored simulation result with ID {result_id}")
            return result_id
            
        except sqlite3.Error as e:
            self.logger.error(f"Error storing simulation result: {e}")
            raise
    
    def update_player_statistics(self, player_name: str, club_name: str, distance: float):
        """Update player statistics with new swing data"""
        try:
            cursor = self.connection.cursor()
            
            # Get current statistics
            cursor.execute("""
                SELECT avg_distance, max_distance, total_swings 
                FROM player_statistics 
                WHERE player_name = ? AND club_name = ?
            """, (player_name, club_name))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing statistics
                avg_distance, max_distance, total_swings = result
                new_total_swings = total_swings + 1
                new_avg_distance = ((avg_distance * total_swings) + distance) / new_total_swings
                new_max_distance = max(max_distance, distance)
                
                cursor.execute("""
                    UPDATE player_statistics 
                    SET avg_distance = ?, max_distance = ?, total_swings = ?, last_updated = ?
                    WHERE player_name = ? AND club_name = ?
                """, (new_avg_distance, new_max_distance, new_total_swings, 
                      datetime.now().isoformat(), player_name, club_name))
            else:
                # Insert new statistics
                cursor.execute("""
                    INSERT INTO player_statistics 
                    (player_name, club_name, avg_distance, max_distance, avg_accuracy, total_swings)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (player_name, club_name, distance, distance, 0.0, 1))
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            self.logger.error(f"Error updating player statistics: {e}")
            raise
    
    def get_player_statistics(self, player_name: str) -> List[Dict[str, Any]]:
        """Get statistics for a specific player"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT club_name, avg_distance, max_distance, total_swings, last_updated
                FROM player_statistics 
                WHERE player_name = ?
                ORDER BY club_name
            """, (player_name,))
            
            results = cursor.fetchall()
            return [
                {
                    'club_name': row[0],
                    'avg_distance': row[1],
                    'max_distance': row[2],
                    'total_swings': row[3],
                    'last_updated': row[4]
                }
                for row in results
            ]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving player statistics: {e}")
            return []
    
    def get_recent_swings(self, player_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent swings for a player"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.timestamp, s.club_name, s.player_name, sr.carry_distance, sr.max_height
                FROM swings s
                LEFT JOIN simulation_results sr ON s.id = sr.swing_id
                WHERE s.player_name = ?
                ORDER BY s.created_at DESC
                LIMIT ?
            """, (player_name, limit))
            
            results = cursor.fetchall()
            return [
                {
                    'timestamp': row[0],
                    'club_name': row[1],
                    'player_name': row[2],
                    'carry_distance': row[3],
                    'max_height': row[4]
                }
                for row in results
            ]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving recent swings: {e}")
            return []
    
    def export_to_csv(self, output_dir: str = "exports") -> str:
        """Export all data to CSV files"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export swings with simulation results
            swings_file = os.path.join(output_dir, f"swings_{timestamp}.csv")
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.timestamp, s.club_name, s.player_name, 
                       sr.carry_distance, sr.max_height, sr.flight_time,
                       sr.ball_speed, sr.launch_angle, sr.spin_rate
                FROM swings s
                LEFT JOIN simulation_results sr ON s.id = sr.swing_id
                ORDER BY s.created_at
            """)
            
            with open(swings_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Club', 'Player', 'Carry Distance', 
                               'Max Height', 'Flight Time', 'Ball Speed', 
                               'Launch Angle', 'Spin Rate'])
                writer.writerows(cursor.fetchall())
            
            # Export player statistics
            stats_file = os.path.join(output_dir, f"player_stats_{timestamp}.csv")
            cursor.execute("""
                SELECT player_name, club_name, avg_distance, max_distance, total_swings
                FROM player_statistics
                ORDER BY player_name, club_name
            """)
            
            with open(stats_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Player', 'Club', 'Avg Distance', 'Max Distance', 'Total Swings'])
                writer.writerows(cursor.fetchall())
            
            self.logger.info(f"Data exported to {output_dir}")
            return output_dir
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create data store
    data_store = GolfDataStore()
    
    # Create a test session
    session_id = data_store.create_session("TestPlayer", "Practice Range", "Sunny, 20°C")
    
    # Store test swing data
    test_swing = {
        'timestamp': int(datetime.now().timestamp() * 1000),
        'club': '7-Iron',
        'player': 'TestPlayer',
        'device_id': 'M5StickCPlus2_001',
        'accel_x': 2.5,
        'accel_y': 1.2,
        'accel_z': 9.8,
        'gyro_x': 50.0,
        'gyro_y': 100.0,
        'gyro_z': 30.0
    }
    
    swing_id = data_store.store_swing_data(session_id, test_swing)
    
    # Store test simulation result
    test_result = {
        'results': {
            'carry_distance': 125.5,
            'max_height': 25.3,
            'flight_time': 4.2,
            'landing_angle': 35.0
        },
        'launch_conditions': {
            'ball_speed': 42.0,
            'launch_angle': 28.0,
            'spin_rate': 6500.0
        },
        'trajectory': []
    }
    
    data_store.store_simulation_result(swing_id, test_result)
    data_store.update_player_statistics("TestPlayer", "7-Iron", 125.5)
    
    # Display statistics
    stats = data_store.get_player_statistics("TestPlayer")
    print("Player Statistics:")
    for stat in stats:
        print(f"  {stat['club_name']}: Avg {stat['avg_distance']:.1f}m, Max {stat['max_distance']:.1f}m")
    
    data_store.close()