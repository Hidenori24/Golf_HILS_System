#include "imu_data_acquisition.h"
#include <M5Unified.h>
#include <M5StickCPlus2.h>
#include "DisplayManager.h"
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
    display_mode = 0; // 0: 通常表示, 1: 2次元グラフ表示
    axis_mode = 0; // 0:xy, 1:yz, 2:xz
    displayManager = new DisplayManager();
}

bool IMUDataAcquisition::initialize() {
    // IMU初期化
    M5.Imu.begin();

    // キャリブレーション
    calibrateIMU();

    // ディスプレイ初期化
    displayManager->clear();

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

    // スイッチ押下検知（A/Bボタン）
    M5.update();
    if (M5.BtnA.wasPressed()) {
        display_mode = (display_mode + 1) % 2; // 0:通常, 1:2次元グラフ
        displayManager->clear();
    }
    if (display_mode == 1 && M5.BtnB.wasPressed()) {
        axis_mode = (axis_mode + 1) % 3; // xy→yz→xz→xy
        displayManager->clear();
    }

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

    if (display_mode == 0) {
        // 通常グラフ
        displayManager->showSwingGraph(data.accel_x, data.accel_y, data.accel_z);
    } else {
        // 2次元加速度グラフ
        displayManager->showAccel2DGraph(data.accel_x, data.accel_y, data.accel_z, axis_mode);
    }

    return data;
}

bool IMUDataAcquisition::detectSwingStart(const SwingData& data) {
    // シンプルなスイング検出（加速度の大きさに基づく）
    float accel_magnitude = sqrt(data.accel_x * data.accel_x +
                                 data.accel_y * data.accel_y +
                                 data.accel_z * data.accel_z);
    
    return accel_magnitude > SWING_THRESHOLD;
}