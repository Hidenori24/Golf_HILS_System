# Golf HILS System Build Instructions

## Overview
This document provides build and setup instructions for both the sensor firmware and simulation software components of the Golf HILS System.

---

## Prerequisites

### Hardware Requirements
- **Sensor Unit**: M5StickC Plus2
- **Simulation Unit**: Raspberry Pi 4 Model B (4GB RAM recommended)
- **Display**: HDMI-compatible monitor/TV
- **Connection**: USB-C to USB-A cable

### Software Requirements
- **Development Environment**: PlatformIO or Arduino IDE
- **Operating System**: Raspberry Pi OS (64-bit recommended)
- **Python**: 3.9 or later

---

## Sensor Firmware Build

### Method 1: Using PlatformIO (Recommended)

1. **Install PlatformIO**
   ```bash
   # Install PlatformIO Core
   pip install platformio
   
   # Or use VS Code extension
   # Install "PlatformIO IDE" extension in VS Code
   ```

2. **Build and Upload**
   ```bash
   cd sensor-firmware/
   
   # Build firmware
   pio run
   
   # Upload to M5StickC Plus2 (connect via USB-C)
   pio run --target upload
   
   # Monitor serial output
   pio device monitor
   ```

### Method 2: Using Arduino IDE

1. **Setup Arduino IDE**
   - Install Arduino IDE 2.0 or later
   - Add ESP32 board support:
     - Go to File → Preferences
     - Add to Additional Board Manager URLs:
       `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Install ESP32 boards via Tools → Board → Boards Manager

2. **Install Libraries**
   - M5StickCPlus2 library
   - ArduinoJson library
   - PubSubClient library

3. **Compile and Upload**
   - Open `examples/golf_swing_monitor.ino`
   - Select Board: "M5Stick-C"
   - Select Port: Your device port
   - Click Upload

### Configuration

Edit the configuration in the main sketch:
```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* MQTT_BROKER = "192.168.1.100";
```

---

## Simulation Software Setup

### Raspberry Pi Setup

1. **Automated Setup (Recommended)**
   ```bash
   cd simulator-py/
   chmod +x setup_raspberry_pi.sh
   ./setup_raspberry_pi.sh
   ```

2. **Manual Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install -y python3 python3-pip python3-venv
   sudo apt install -y python3-numpy python3-scipy python3-matplotlib
   sudo apt install -y python3-pygame python3-serial sqlite3
   
   # Create virtual environment
   cd simulator-py/
   python3 -m venv venv
   source venv/bin/activate
   
   # Install Python packages
   pip install -r requirements.txt
   
   # Setup directories
   mkdir -p data/exports trajectories logs
   
   # Add user to dialout group for serial access
   sudo usermod -a -G dialout $USER
   ```

### Development Environment Setup

For development on other platforms:

**Ubuntu/Debian:**
```bash
sudo apt install python3-dev python3-venv libatlas-base-dev
cd simulator-py/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**macOS:**
```bash
brew install python3
cd simulator-py/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
cd simulator-py\
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running the System

### Start Simulation Software

```bash
cd simulator-py/
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Run with default settings
python main.py

# Run with custom settings
python main.py --port /dev/ttyUSB0 --baud 115200 --display live

# Run in headless mode
python main.py --display headless
```

### Command Line Options

```
--port PORT         Serial port (default: /dev/ttyUSB0)
--baud BAUD         Baud rate (default: 115200)
--display MODE      Display mode: live, headless, both (default: live)
--log-level LEVEL   Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
```

### Start Sensor Unit

1. Power on M5StickC Plus2 (hold C button for 2 seconds)
2. The device will show "Golf HILS Sensor" and initialization status
3. Use A button to select club, B button to select player
4. Take a golf swing to generate data

---

## Testing

### Sensor Firmware Testing

```bash
cd sensor-firmware/
pio test
```

### Simulation Software Testing

```bash
cd simulator-py/
source venv/bin/activate
pytest tests/ -v
```

### Integration Testing

1. Start simulation software
2. Connect sensor unit via USB
3. Take test swings
4. Verify data reception and trajectory calculation

---

## Example Usage

### Trajectory Analysis Example

```bash
cd simulator-py/
source venv/bin/activate
python examples/trajectory_analysis_example.py
```

This will:
- Generate sample swing data
- Analyze multiple club types
- Create trajectory visualizations
- Store results in database
- Export data to CSV

---

## Configuration

### Sensor Configuration

Edit `sensor-firmware/config/sensor_config.env`:
```bash
WIFI_SSID=YOUR_NETWORK
WIFI_PASSWORD=YOUR_PASSWORD
MQTT_BROKER_IP=192.168.1.100
SWING_DETECTION_THRESHOLD=2.0
```

### Simulator Configuration

Edit `simulator-py/config/simulator_config.yaml`:
```yaml
serial:
  port: "/dev/ttyUSB0"
  baud_rate: 115200

display:
  mode: "live"
  screen_size: [1024, 768]

database:
  path: "golf_hils_data.db"
```

---

## Troubleshooting

### Common Issues

**Serial Port Access Denied:**
```bash
sudo usermod -a -G dialout $USER
# Then logout and login again
```

**M5StickC Plus2 Not Detected:**
- Check USB cable (data capable, not just charging)
- Press reset button on M5StickC Plus2
- Try different USB port

**Display Issues on Raspberry Pi:**
```bash
# Enable GPU memory split
sudo raspi-config
# Advanced Options → Memory Split → 128
```

**Python Package Installation Errors:**
```bash
# Update pip
pip install --upgrade pip

# Install build dependencies
sudo apt install python3-dev build-essential
```

### Performance Optimization

**For Raspberry Pi:**
```bash
# Increase GPU memory
echo "gpu_mem=128" | sudo tee -a /boot/config.txt

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

---

## System Service (Optional)

To run the simulator as a system service:

```bash
# Enable service
sudo systemctl enable golf-hils.service

# Start service
sudo systemctl start golf-hils.service

# Check status
sudo systemctl status golf-hils.service

# View logs
sudo journalctl -u golf-hils.service -f
```

---

## Development Workflow

### Sensor Firmware Development

1. Make changes to source code
2. Build and test locally:
   ```bash
   pio run
   pio test
   ```
3. Upload to device:
   ```bash
   pio run --target upload
   ```
4. Monitor serial output:
   ```bash
   pio device monitor
   ```

### Simulation Software Development

1. Make changes to Python code
2. Run tests:
   ```bash
   pytest tests/ -v
   ```
3. Test with example data:
   ```bash
   python examples/trajectory_analysis_example.py
   ```
4. Test full system integration

---

## Documentation Generation

### API Documentation

```bash
cd simulator-py/
source venv/bin/activate
pip install sphinx
sphinx-quickstart docs/
sphinx-build -b html docs/ docs/_build/
```

### Code Documentation

```bash
# Generate firmware documentation
cd sensor-firmware/
doxygen Doxyfile

# Generate Python documentation
cd simulator-py/
pdoc --html . --output-dir docs/
```

---

For additional support and updates, check the project repository README and issues section.