#ifndef IMU_DATA_ACQUISITION_H
#define IMU_DATA_ACQUISITION_H

#include <Arduino.h>

// Swing detection threshold (in G)
#define SWING_THRESHOLD 2.0

// Data structure for swing measurements
struct SwingData {
    float accel_x, accel_y, accel_z;    // Acceleration (G)
    float gyro_x, gyro_y, gyro_z;       // Angular velocity (dps)
    unsigned long timestamp;             // Timestamp in milliseconds
};

class IMUDataAcquisition {
private:
    // Calibration offsets
    float accel_offset_x, accel_offset_y, accel_offset_z;
    float gyro_offset_x, gyro_offset_y, gyro_offset_z;
    
    void calibrateIMU();

public:
    IMUDataAcquisition();
    
    // Initialize IMU sensor
    bool initialize();
    
    // Read current swing data
    SwingData readSwingData();
    
    // Detect if swing has started based on acceleration threshold
    bool detectSwingStart(const SwingData& data);
};

#endif // IMU_DATA_ACQUISITION_H