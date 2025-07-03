#ifndef SWING_DATA_TRANSMITTER_H
#define SWING_DATA_TRANSMITTER_H

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "../SensorManager/imu_data_acquisition.h"

enum TransmissionMode {
    SERIAL_MODE,
    MQTT_MODE,
    DUAL_MODE
};

class SwingDataTransmitter {
private:
    bool is_serial_initialized;
    bool is_wifi_connected;
    unsigned long baud_rate;
    
    WiFiClient wifi_client;
    PubSubClient mqtt_client;
    
    String createSwingDataPacket(const SwingData& swing_data, 
                               const String& club_name, 
                               const String& player_name);
    
    bool sendViaSerial(const String& data);
    bool sendViaMQTT(const String& data, const char* topic);

public:
    SwingDataTransmitter();
    
    // Initialize communication channels
    bool initializeSerial(unsigned long baud = 115200);
    bool initializeWiFi(const char* ssid, const char* password);
    bool initializeMQTT(const char* broker, int port = 1883);
    
    // Send swing data using specified mode
    bool sendSwingData(const SwingData& swing_data, 
                      const String& club_name, 
                      const String& player_name,
                      TransmissionMode mode = SERIAL_MODE);
    
    // Maintain active connections
    void maintainConnections();
};

#endif // SWING_DATA_TRANSMITTER_H