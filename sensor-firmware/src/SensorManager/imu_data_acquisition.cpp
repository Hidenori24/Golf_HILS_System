#include "imu_data_acquisition.h"
#include <M5Unified.h>
#include <M5StickCPlus2.h>
#include <math.h>

// 色定義（未定義の場合のみ）
#ifndef RED
#define RED     0xF800
#endif
#ifndef GREEN
#define GREEN   0x07E0
#endif
#ifndef BLUE
#define BLUE    0x001F
#endif

IMUDataAcquisition::IMUDataAcquisition() {
    accel_offset_x = 0.0;
    accel_offset_y = 0.0;
    accel_offset_z = 0.0;
    gyro_offset_x = 0.0;
    gyro_offset_y = 0.0;
    gyro_offset_z = 0.0;
}

bool IMUDataAcquisition::initialize() {
    // IMU初期化
    M5.Imu.begin();

    // キャリブレーション
    calibrateIMU();

    // ディスプレイ初期化
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);

    return true;
}

void IMUDataAcquisition::calibrateIMU() {
    float sum_ax = 0, sum_ay = 0, sum_az = 0;
    float sum_gx = 0, sum_gy = 0, sum_gz = 0;
    const int samples = 100;

    for (int i = 0; i < samples; i++) {
        float ax, ay, az, gx, gy, gz;
        M5.Imu.getAccelData(&ax, &ay, &az);
        M5.Imu.getGyroData(&gx, &gy, &gz);

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
    accel_offset_z = sum_az / samples - 1.0; // Z軸は1G分引く
    gyro_offset_x = sum_gx / samples;
    gyro_offset_y = sum_gy / samples;
    gyro_offset_z = sum_gz / samples;
}

SwingData IMUDataAcquisition::readSwingData() {
    SwingData data;


    float ax, ay, az, gx, gy, gz;
    M5.Imu.getAccelData(&ax, &ay, &az);
    M5.Imu.getGyroData(&gx, &gy, &gz);

    data.accel_x = ax - accel_offset_x;
    data.accel_y = ay - accel_offset_y;
    data.accel_z = az - accel_offset_z;
    data.gyro_x = gx - gyro_offset_x;
    data.gyro_y = gy - gyro_offset_y;
    data.gyro_z = gz - gyro_offset_z;

    data.timestamp = millis();

    // --- グラフ表示 ---
    static int x = 0;
    int y0 = 40, y_scale = 20;
    if (x == 0) {
        M5.Lcd.fillRect(0, y0 - 30, 240, 60, BLACK);
    }
    int ax_y = y0 - (int)(data.accel_x * y_scale);
    int ay_y = y0 - (int)(data.accel_y * y_scale);
    int az_y = y0 - (int)(data.accel_z * y_scale);
    if (ax_y < 0) ax_y = 0; if (ax_y > 79) ax_y = 79;
    if (ay_y < 0) ay_y = 0; if (ay_y > 79) ay_y = 79;
    if (az_y < 0) az_y = 0; if (az_y > 79) az_y = 79;

    M5.Lcd.drawPixel(x, ax_y, RED);
    M5.Lcd.drawPixel(x, ay_y, GREEN);
    M5.Lcd.drawPixel(x, az_y, BLUE);

    x++;
    if (x >= 240) x = 0;

    M5.Lcd.setCursor(0, 0);
    M5.Lcd.printf("ax:%.2f ay:%.2f az:%.2f", data.accel_x, data.accel_y, data.accel_z);

    return data;
}

bool IMUDataAcquisition::detectSwingStart(const SwingData& data) {
    // シンプルなスイング検出（加速度の大きさに基づく）
    float accel_magnitude = sqrt(data.accel_x * data.accel_x +
                                 data.accel_y * data.accel_y +
                                 data.accel_z * data.accel_z);
    
    return accel_magnitude > SWING_THRESHOLD;
}