#!/bin/bash

# Golf HILS System Setup Script for Raspberry Pi
# This script sets up the development environment for the simulator

echo "=== Golf HILS System Setup ==="
echo "Setting up Raspberry Pi environment..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
echo "Installing Python and development tools..."
sudo apt install -y python3 python3-pip python3-venv git

# Install system dependencies for graphics and serial communication
echo "Installing system dependencies..."
sudo apt install -y \
    python3-dev \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    python3-pygame \
    python3-serial \
    sqlite3 \
    libatlas-base-dev \
    libopenjp2-7 \
    libtiff5 \
    libxcb1 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libgl1-mesa-glx

# Create virtual environment
echo "Creating Python virtual environment..."
cd ~/Golf_HILS_System/simulator-py
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
echo "Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup directories
echo "Creating required directories..."
mkdir -p data/exports
mkdir -p trajectories
mkdir -p logs

# Set permissions for serial port access
echo "Setting up serial port permissions..."
sudo usermod -a -G dialout $USER

# Create systemd service (optional)
echo "Creating systemd service..."
sudo tee /etc/systemd/system/golf-hils.service > /dev/null <<EOF
[Unit]
Description=Golf HILS Simulator
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Golf_HILS_System/simulator-py
Environment=PATH=/home/pi/Golf_HILS_System/simulator-py/venv/bin
ExecStart=/home/pi/Golf_HILS_System/simulator-py/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable auto-start (optional)
# sudo systemctl enable golf-hils.service

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the simulator:"
echo "  cd ~/Golf_HILS_System/simulator-py"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "To enable auto-start on boot:"
echo "  sudo systemctl enable golf-hils.service"
echo "  sudo systemctl start golf-hils.service"
echo ""
echo "Note: You may need to reboot for serial port permissions to take effect."