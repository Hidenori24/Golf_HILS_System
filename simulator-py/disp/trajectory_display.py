"""
Golf HILS System - Display Manager

This module handles the graphical display of simulation results, trajectory visualization,
and player statistics using Matplotlib and Pygame for Raspberry Pi display output.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from typing import List, Dict, Any, Optional
import pygame
import logging
from datetime import datetime

class TrajectoryVisualizer:
    """Handles 2D trajectory visualization using Matplotlib"""
    
    def __init__(self, figure_size: tuple = (12, 8)):
        self.figure_size = figure_size
        self.logger = logging.getLogger(__name__)
        
        # Setup matplotlib for headless operation on Raspberry Pi
        plt.style.use('seaborn-v0_8-darkgrid')
        self.fig = None
        self.ax = None
    
    def create_trajectory_plot(self, trajectory_data: List[Dict], 
                             simulation_results: Dict[str, Any]) -> plt.Figure:
        """Create a 2D trajectory plot"""
        
        self.fig, self.ax = plt.subplots(figsize=self.figure_size)
        
        # Extract trajectory points
        x_coords = [point['x'] for point in trajectory_data]
        y_coords = [point['y'] for point in trajectory_data]
        
        # Plot trajectory
        self.ax.plot(x_coords, y_coords, 'b-', linewidth=2, label='Ball Trajectory')
        self.ax.fill_between(x_coords, 0, y_coords, alpha=0.3, color='lightblue')
        
        # Mark key points
        max_height_idx = np.argmax(y_coords)
        self.ax.plot(x_coords[max_height_idx], y_coords[max_height_idx], 
                    'ro', markersize=8, label=f'Peak: {y_coords[max_height_idx]:.1f}m')
        
        # Landing point
        self.ax.plot(x_coords[-1], 0, 'go', markersize=8, 
                    label=f'Landing: {x_coords[-1]:.1f}m')
        
        # Formatting
        self.ax.set_xlabel('Distance (meters)', fontsize=12)
        self.ax.set_ylabel('Height (meters)', fontsize=12)
        self.ax.set_title('Golf Ball Trajectory Analysis', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        # Add statistics text box
        stats_text = self._create_stats_text(simulation_results)
        self.ax.text(0.02, 0.98, stats_text, transform=self.ax.transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', 
                    facecolor='wheat', alpha=0.8), fontsize=10)
        
        # Set equal aspect ratio with some padding
        self.ax.set_xlim(-10, max(x_coords) * 1.1)
        self.ax.set_ylim(-5, max(y_coords) * 1.2)
        
        plt.tight_layout()
        return self.fig
    
    def _create_stats_text(self, results: Dict[str, Any]) -> str:
        """Create formatted statistics text"""
        stats = results.get('results', {})
        launch = results.get('launch_conditions', {})
        
        text = f"""Shot Statistics:
Carry: {stats.get('carry_distance', 0):.1f} m
Max Height: {stats.get('max_height', 0):.1f} m
Flight Time: {stats.get('flight_time', 0):.1f} s
Ball Speed: {launch.get('ball_speed', 0):.1f} m/s
Launch Angle: {launch.get('launch_angle', 0):.1f}°
Spin Rate: {launch.get('spin_rate', 0):.0f} rpm"""
        
        return text
    
    def save_plot(self, filename: str = None) -> str:
        """Save the current plot to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trajectory_{timestamp}.png"
        
        if self.fig:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
            self.logger.info(f"Trajectory plot saved as {filename}")
            return filename
        else:
            self.logger.error("No plot to save")
            return ""

class LiveDisplayManager:
    """Manages live display using Pygame for Raspberry Pi"""
    
    def __init__(self, screen_size: tuple = (1024, 768)):
        self.screen_size = screen_size
        self.logger = logging.getLogger(__name__)
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Golf HILS Live Display")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.heading_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def display_waiting_screen(self):
        """Display waiting for swing screen"""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = self.title_font.render("Golf HILS System", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_size[0]//2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Status
        status_text = self.heading_font.render("Waiting for Swing...", True, self.GREEN)
        status_rect = status_text.get_rect(center=(self.screen_size[0]//2, 200))
        self.screen.blit(status_text, status_rect)
        
        # Instructions
        instructions = [
            "1. Select club on sensor unit",
            "2. Take your swing",
            "3. View results on this screen"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.text_font.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(self.screen_size[0]//2, 300 + i*40))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def display_swing_detected(self, player_name: str, club_name: str):
        """Display swing detection screen"""
        self.screen.fill(self.RED)
        
        # Big notification
        swing_text = self.title_font.render("SWING DETECTED!", True, self.WHITE)
        swing_rect = swing_text.get_rect(center=(self.screen_size[0]//2, 200))
        self.screen.blit(swing_text, swing_rect)
        
        # Player and club info
        player_text = self.heading_font.render(f"Player: {player_name}", True, self.WHITE)
        player_rect = player_text.get_rect(center=(self.screen_size[0]//2, 300))
        self.screen.blit(player_text, player_rect)
        
        club_text = self.heading_font.render(f"Club: {club_name}", True, self.WHITE)
        club_rect = club_text.get_rect(center=(self.screen_size[0]//2, 350))
        self.screen.blit(club_text, club_rect)
        
        # Processing message
        processing_text = self.text_font.render("Processing swing data...", True, self.YELLOW)
        processing_rect = processing_text.get_rect(center=(self.screen_size[0]//2, 450))
        self.screen.blit(processing_text, processing_rect)
        
        pygame.display.flip()
    
    def display_simulation_results(self, simulation_results: Dict[str, Any]):
        """Display simulation results"""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = self.title_font.render("Shot Results", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_size[0]//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Extract data
        results = simulation_results.get('results', {})
        launch = simulation_results.get('launch_conditions', {})
        club_name = simulation_results.get('club_used', 'Unknown')
        
        # Club used
        club_text = self.heading_font.render(f"Club: {club_name}", True, self.YELLOW)
        club_rect = club_text.get_rect(center=(self.screen_size[0]//2, 120))
        self.screen.blit(club_text, club_rect)
        
        # Main results - two columns
        left_x = self.screen_size[0] // 4
        right_x = 3 * self.screen_size[0] // 4
        
        # Left column
        left_results = [
            f"Carry Distance: {results.get('carry_distance', 0):.1f} m",
            f"Max Height: {results.get('max_height', 0):.1f} m",
            f"Flight Time: {results.get('flight_time', 0):.1f} s",
        ]
        
        for i, result in enumerate(left_results):
            text = self.text_font.render(result, True, self.WHITE)
            text_rect = text.get_rect(center=(left_x, 200 + i*40))
            self.screen.blit(text, text_rect)
        
        # Right column
        right_results = [
            f"Ball Speed: {launch.get('ball_speed', 0):.1f} m/s",
            f"Launch Angle: {launch.get('launch_angle', 0):.1f}°",
            f"Spin Rate: {launch.get('spin_rate', 0):.0f} rpm",
        ]
        
        for i, result in enumerate(right_results):
            text = self.text_font.render(result, True, self.WHITE)
            text_rect = text.get_rect(center=(right_x, 200 + i*40))
            self.screen.blit(text, text_rect)
        
        # Simple trajectory visualization
        self._draw_simple_trajectory(simulation_results.get('trajectory', []))
        
        # Footer
        footer_text = self.small_font.render("Waiting for next swing...", True, self.GREEN)
        footer_rect = footer_text.get_rect(center=(self.screen_size[0]//2, self.screen_size[1]-30))
        self.screen.blit(footer_text, footer_rect)
        
        pygame.display.flip()
    
    def _draw_simple_trajectory(self, trajectory_data: List[Dict]):
        """Draw a simple trajectory visualization"""
        if not trajectory_data:
            return
        
        # Define drawing area
        draw_x = 50
        draw_y = 400
        draw_width = self.screen_size[0] - 100
        draw_height = 200
        
        # Extract coordinates and normalize
        x_coords = [point['x'] for point in trajectory_data]
        y_coords = [point['y'] for point in trajectory_data]
        
        if not x_coords or not y_coords:
            return
        
        max_x = max(x_coords)
        max_y = max(y_coords)
        
        if max_x == 0 or max_y == 0:
            return
        
        # Draw ground line
        pygame.draw.line(self.screen, self.GREEN, 
                        (draw_x, draw_y + draw_height), 
                        (draw_x + draw_width, draw_y + draw_height), 3)
        
        # Draw trajectory
        points = []
        for i in range(len(x_coords)):
            screen_x = draw_x + (x_coords[i] / max_x) * draw_width
            screen_y = draw_y + draw_height - (y_coords[i] / max_y) * draw_height
            points.append((int(screen_x), int(screen_y)))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, self.BLUE, False, points, 3)
        
        # Mark peak and landing
        if points:
            # Peak (highest point)
            peak_idx = np.argmax(y_coords)
            if peak_idx < len(points):
                pygame.draw.circle(self.screen, self.RED, points[peak_idx], 8)
            
            # Landing
            pygame.draw.circle(self.screen, self.GREEN, points[-1], 8)
    
    def display_player_statistics(self, player_stats: List[Dict[str, Any]]):
        """Display player statistics screen"""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = self.title_font.render("Player Statistics", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_size[0]//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Headers
        headers = ["Club", "Avg Distance", "Max Distance", "Total Swings"]
        header_y = 150
        col_width = self.screen_size[0] // len(headers)
        
        for i, header in enumerate(headers):
            text = self.heading_font.render(header, True, self.YELLOW)
            text_rect = text.get_rect(center=(col_width//2 + i*col_width, header_y))
            self.screen.blit(text, text_rect)
        
        # Statistics data
        start_y = 200
        for i, stat in enumerate(player_stats[:15]):  # Limit to screen space
            y_pos = start_y + i * 30
            
            # Club name
            club_text = self.text_font.render(stat['club_name'], True, self.WHITE)
            club_rect = club_text.get_rect(center=(col_width//2, y_pos))
            self.screen.blit(club_text, club_rect)
            
            # Average distance
            avg_text = self.text_font.render(f"{stat['avg_distance']:.1f}m", True, self.WHITE)
            avg_rect = avg_text.get_rect(center=(col_width//2 + col_width, y_pos))
            self.screen.blit(avg_text, avg_rect)
            
            # Max distance
            max_text = self.text_font.render(f"{stat['max_distance']:.1f}m", True, self.WHITE)
            max_rect = max_text.get_rect(center=(col_width//2 + 2*col_width, y_pos))
            self.screen.blit(max_text, max_rect)
            
            # Total swings
            total_text = self.text_font.render(str(stat['total_swings']), True, self.WHITE)
            total_rect = total_text.get_rect(center=(col_width//2 + 3*col_width, y_pos))
            self.screen.blit(total_text, total_rect)
        
        pygame.display.flip()
    
    def handle_events(self) -> bool:
        """Handle Pygame events, return False to quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
        return True
    
    def cleanup(self):
        """Clean up Pygame resources"""
        pygame.quit()

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test trajectory visualizer
    visualizer = TrajectoryVisualizer()
    
    # Mock trajectory data
    mock_trajectory = [
        {'x': i, 'y': -0.05*i**2 + 2*i} for i in range(0, 100, 2)
    ]
    
    mock_results = {
        'results': {
            'carry_distance': 98.0,
            'max_height': 20.0,
            'flight_time': 4.5,
            'landing_angle': 35.0
        },
        'launch_conditions': {
            'ball_speed': 45.0,
            'launch_angle': 25.0,
            'spin_rate': 6000.0
        },
        'club_used': '7-Iron'
    }
    
    fig = visualizer.create_trajectory_plot(mock_trajectory, mock_results)
    visualizer.save_plot("test_trajectory.png")
    plt.show()
    
    # Test live display manager
    display_manager = LiveDisplayManager()
    
    # Show different screens for testing
    display_manager.display_waiting_screen()
    pygame.time.wait(2000)
    
    display_manager.display_swing_detected("TestPlayer", "7-Iron")
    pygame.time.wait(2000)
    
    display_manager.display_simulation_results(mock_results)
    pygame.time.wait(3000)
    
    display_manager.cleanup()