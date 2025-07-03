#include "swing_data_transmitter.h"
#include <ArduinoJson.h>

SwingDataTransmitter::SwingDataTransmitter() {
    is_serial_initialized = false;
    is_wifi_connected = false;
    baud_rate = 115200;
}

bool SwingDataTransmitter::initializeSerial(unsigned long baud) {
    baud_rate = baud;
    Serial.begin(baud_rate);
    
    // Wait for serial port to initialize
    delay(1000);
    
    is_serial_initialized = true;
    return true;
}

bool SwingDataTransmitter::initializeWiFi(const char* ssid, const char* password) {
    WiFi.begin(ssid, password);
    
    // Wait for connection
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        is_wifi_connected = true;
        return true;
    }
    
    return false;
}

bool SwingDataTransmitter::initializeMQTT(const char* broker, int port) {
    if (!is_wifi_connected) {
        return false;
    }
    
    mqtt_client.setServer(broker, port);
    
    // Connect to MQTT broker
    if (mqtt_client.connect("M5StickCPlus2_Golf_Sensor")) {
        return true;
    }
    
    return false;
}

String SwingDataTransmitter::createSwingDataPacket(const SwingData& swing_data, 
                                                  const String& club_name, 
                                                  const String& player_name) {
    // Create JSON packet
    StaticJsonDocument<512> doc;
    
    // Add sensor data
    doc["timestamp"] = swing_data.timestamp;
    doc["accel_x"] = swing_data.accel_x;
    doc["accel_y"] = swing_data.accel_y;
    doc["accel_z"] = swing_data.accel_z;
    doc["gyro_x"] = swing_data.gyro_x;
    doc["gyro_y"] = swing_data.gyro_y;
    doc["gyro_z"] = swing_data.gyro_z;
    
    // Add metadata
    doc["club"] = club_name;
    doc["player"] = player_name;
    doc["device_id"] = "M5StickCPlus2_001";
    
    // Serialize to string
    String packet;
    serializeJson(doc, packet);
    
    return packet;
}

bool SwingDataTransmitter::sendViaSerial(const String& data) {
    if (!is_serial_initialized) {
        return false;
    }
    
    Serial.println(data);
    return true;
}

bool SwingDataTransmitter::sendViaMQTT(const String& data, const char* topic) {
    if (!mqtt_client.connected()) {
        return false;
    }
    
    return mqtt_client.publish(topic, data.c_str());
}

bool SwingDataTransmitter::sendSwingData(const SwingData& swing_data, 
                                        const String& club_name, 
                                        const String& player_name,
                                        TransmissionMode mode) {
    String packet = createSwingDataPacket(swing_data, club_name, player_name);
    
    switch (mode) {
        case SERIAL_MODE:
            return sendViaSerial(packet);
            
        case MQTT_MODE:
            return sendViaMQTT(packet, "golf/swing_data");
            
        case DUAL_MODE:
            bool serial_success = sendViaSerial(packet);
            bool mqtt_success = sendViaMQTT(packet, "golf/swing_data");
            return serial_success || mqtt_success;
    }
    
    return false;
}

void SwingDataTransmitter::maintainConnections() {
    // Maintain MQTT connection
    if (is_wifi_connected && !mqtt_client.connected()) {
        mqtt_client.connect("M5StickCPlus2_Golf_Sensor");
    }
    
    if (mqtt_client.connected()) {
        mqtt_client.loop();
    }
}