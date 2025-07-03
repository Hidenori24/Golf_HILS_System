#include "imu_data_acquisition.h"
#include <M5StickCPlus2.h>

IMUDataAcquisition::IMUDataAcquisition() {
    // Initialize IMU calibration values
    accel_offset_x = 0.0;
    accel_offset_y = 0.0;
    accel_offset_z = 0.0;
    gyro_offset_x = 0.0;
    gyro_offset_y = 0.0;
    gyro_offset_z = 0.0;
}

bool IMUDataAcquisition::initialize() {
    // Initialize M5StickC Plus2 IMU (MPU6886)
    M5.IMU.Init();
    
    // Perform initial calibration
    calibrateIMU();
    
    return true;
}

void IMUDataAcquisition::calibrateIMU() {
    // Calibration routine - collect offset values
    float sum_ax = 0, sum_ay = 0, sum_az = 0;
    float sum_gx = 0, sum_gy = 0, sum_gz = 0;
    
    const int samples = 100;
    
    for (int i = 0; i < samples; i++) {
        float ax, ay, az, gx, gy, gz;
        M5.IMU.getAccelData(&ax, &ay, &az);
        M5.IMU.getGyroData(&gx, &gy, &gz);
        
        sum_ax += ax;
        sum_ay += ay;
        sum_az += az;
        sum_gx += gx;
        sum_gy += gy;
        sum_gz += gz;
        
        delay(10);
    }
    
    accel_offset_x = sum_ax / samples;
    accel_offset_y = sum_ay / samples;
    accel_offset_z = sum_az / samples - 1.0; // Subtract 1G for Z-axis
    gyro_offset_x = sum_gx / samples;
    gyro_offset_y = sum_gy / samples;
    gyro_offset_z = sum_gz / samples;
}

SwingData IMUDataAcquisition::readSwingData() {
    SwingData data;
    
    // Read raw IMU data
    float ax, ay, az, gx, gy, gz;
    M5.IMU.getAccelData(&ax, &ay, &az);
    M5.IMU.getGyroData(&gx, &gy, &gz);
    
    // Apply calibration offsets
    data.accel_x = ax - accel_offset_x;
    data.accel_y = ay - accel_offset_y;
    data.accel_z = az - accel_offset_z;
    data.gyro_x = gx - gyro_offset_x;
    data.gyro_y = gy - gyro_offset_y;
    data.gyro_z = gz - gyro_offset_z;
    
    // Add timestamp
    data.timestamp = millis();
    
    return data;
}

bool IMUDataAcquisition::detectSwingStart(const SwingData& data) {
    // Simple swing detection based on acceleration magnitude
    float accel_magnitude = sqrt(data.accel_x * data.accel_x + 
                                data.accel_y * data.accel_y + 
                                data.accel_z * data.accel_z);
    
    return accel_magnitude > SWING_THRESHOLD;
}