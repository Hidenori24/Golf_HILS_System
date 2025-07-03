/*
 * Golf HILS Sensor Unit - Main Program
 * 
 * This is the main entry point for the M5StickC Plus2 Golf HILS sensor unit.
 * It integrates IMU data acquisition, user input handling, and data transmission
 * to create a complete golf swing monitoring system.
 * 
 * Hardware: M5StickC Plus2
 * - IMU: MPU6886 (accelerometer + gyroscope)
 * - Display: 1.14 inch LCD
 * - Buttons: A, B, C (power)
 * - Communication: WiFi, USB Serial
 */

#include <M5StickCPlus2.h>
#include "src/SensorManager/imu_data_acquisition.h"
#include "src/InputManager/golf_club_selector.h"
#include "src/CommManager/swing_data_transmitter.h"

// Component instances
IMUDataAcquisition imu_sensor;
GolfClubSelector club_selector;
SwingDataTransmitter data_transmitter;

// Configuration
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* MQTT_BROKER = "192.168.1.100";  // Replace with your broker IP
const int MQTT_PORT = 1883;

// State management
bool swing_in_progress = false;
unsigned long swing_start_time = 0;
const unsigned long SWING_DURATION_MS = 2000;  // Record for 2 seconds after swing detection

void setup() {
    // Initialize M5StickC Plus2
    M5.begin();
    M5.Lcd.setRotation(3);
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE);
    M5.Lcd.setTextSize(1);
    
    // Display startup message
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.println("Golf HILS Sensor");
    M5.Lcd.setCursor(10, 30);
    M5.Lcd.println("Initializing...");
    
    // Initialize components
    if (!imu_sensor.initialize()) {
        M5.Lcd.setCursor(10, 50);
        M5.Lcd.println("IMU Init Failed!");
        while(1) delay(1000);
    }
    
    if (!club_selector.initialize()) {
        M5.Lcd.setCursor(10, 50);
        M5.Lcd.println("Input Init Failed!");
        while(1) delay(1000);
    }
    
    // Initialize serial communication
    if (!data_transmitter.initializeSerial(115200)) {
        M5.Lcd.setCursor(10, 50);
        M5.Lcd.println("Serial Init Failed!");
        while(1) delay(1000);
    }
    
    // Initialize WiFi (optional)
    M5.Lcd.setCursor(10, 50);
    M5.Lcd.println("Connecting WiFi...");
    if (data_transmitter.initializeWiFi(WIFI_SSID, WIFI_PASSWORD)) {
        M5.Lcd.setCursor(10, 70);
        M5.Lcd.println("WiFi Connected");
        
        // Initialize MQTT (optional)
        if (data_transmitter.initializeMQTT(MQTT_BROKER, MQTT_PORT)) {
            M5.Lcd.setCursor(10, 90);
            M5.Lcd.println("MQTT Connected");
        }
    } else {
        M5.Lcd.setCursor(10, 70);
        M5.Lcd.println("WiFi Failed - Serial Only");
    }
    
    delay(2000);
    
    // Show ready message
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(10, 30);
    M5.Lcd.println("Ready for Golf!");
    M5.Lcd.setCursor(10, 50);
    M5.Lcd.println("A: Select Club");
    M5.Lcd.setCursor(10, 70);
    M5.Lcd.println("B: Select Player");
}

void loop() {
    // Update M5 system
    M5.update();
    
    // Update input handling
    club_selector.update();
    
    // Maintain communication connections
    data_transmitter.maintainConnections();
    
    // Read current IMU data
    SwingData current_data = imu_sensor.readSwingData();
    
    // Check for swing detection
    if (!swing_in_progress && imu_sensor.detectSwingStart(current_data)) {
        // Swing detected - start recording
        swing_in_progress = true;
        swing_start_time = millis();
        
        // Visual feedback
        M5.Lcd.fillScreen(RED);
        M5.Lcd.setCursor(10, 30);
        M5.Lcd.setTextColor(WHITE);
        M5.Lcd.println("SWING DETECTED!");
        
        // Send initial swing data
        String club_name = club_selector.getCurrentClubName();
        String player_name = club_selector.getCurrentPlayerName();
        data_transmitter.sendSwingData(current_data, club_name, player_name, DUAL_MODE);
    }
    
    // Continue recording during swing
    if (swing_in_progress) {
        String club_name = club_selector.getCurrentClubName();
        String player_name = club_selector.getCurrentPlayerName();
        
        // Send data at high frequency during swing
        data_transmitter.sendSwingData(current_data, club_name, player_name, DUAL_MODE);
        
        // Check if swing recording period is complete
        if (millis() - swing_start_time > SWING_DURATION_MS) {
            swing_in_progress = false;
            
            // Visual feedback - swing complete
            M5.Lcd.fillScreen(GREEN);
            M5.Lcd.setCursor(10, 30);
            M5.Lcd.setTextColor(WHITE);
            M5.Lcd.println("Swing Complete!");
            delay(1000);
            
            // Return to ready state
            M5.Lcd.fillScreen(BLACK);
            M5.Lcd.setCursor(10, 30);
            M5.Lcd.println("Ready for Golf!");
            M5.Lcd.setCursor(10, 50);
            M5.Lcd.println("A: Select Club");
            M5.Lcd.setCursor(10, 70);
            M5.Lcd.println("B: Select Player");
        }
    }
    
    // Small delay to prevent overwhelming the system
    delay(swing_in_progress ? 10 : 50);  // Higher frequency during swing
}