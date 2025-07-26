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
    display_mode = 0; // 0: 通常表示, 1: 2次元加速度グラフ
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

    displayManager->clear();
    displayManager->showMessage("Calibrating...");

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

    // 加速度のオフセット（重力補正なし - 静止状態の値をそのまま使用）
    accel_offset_x = sum_ax / samples;
    accel_offset_y = sum_ay / samples;
    accel_offset_z = sum_az / samples; // 重力分は引かない
    
    // ジャイロのオフセット
    gyro_offset_x = sum_gx / samples;
    gyro_offset_y = sum_gy / samples;
    gyro_offset_z = sum_gz / samples;
}

/**
 * ボタン操作・画面遷移・機能一覧
 *
 * Aボタン短押し：画面モード切替（通常グラフ ⇔ 2次元加速度グラフ）
 * Bボタン短押し：2次元グラフ表示時、軸切替（xy → yz → xz → ...）
 * Bボタン長押し（1秒以上）：
 *   - 通常グラフ時：キャリブレーション（静止状態でオフセット再取得）
 *   - 2次元グラフ時：軸リセット（xy軸に戻す）
 *
 * 各画面の表示内容：
 *   - 通常グラフ：加速度グラフ（3軸）+ 生データ表示
 *   - 2次元加速度グラフ：xy/yz/xzの2軸加速度を中心±で表示
 */
SwingData IMUDataAcquisition::readSwingData() {
    SwingData data;

    // スイッチ押下検知（A/B/Cボタン）
    M5.update();
    if (M5.BtnA.wasPressed()) {
        display_mode = (display_mode + 1) % 2; // 0:通常, 1:加速度2次元
        displayManager->clear();
    }
    if (display_mode == 1 && M5.BtnB.wasPressed()) {
        axis_mode = (axis_mode + 1) % 3; // xy→yz→xz→xy
        displayManager->clear();
    }
    // 通常表示時にB長押しでキャリブレーション
    if (display_mode == 0 && M5.BtnB.pressedFor(1000)) {
        calibrateIMU();
        displayManager->clear();
        displayManager->showMessage("Calibrated!");
    }
    // 2次元グラフ時にB長押しで軸リセット
    if (display_mode == 1 && M5.BtnB.pressedFor(1000)) {
        axis_mode = 0; // xy軸に戻す
        displayManager->clear();
    }

    float ax, ay, az, gx, gy, gz;
    M5.Imu.getAccelData(&ax, &ay, &az);  // 単位: G（重力加速度）
    M5.Imu.getGyroData(&gx, &gy, &gz);  // 単位: deg/s（角速度）

    // 補正値（重力除去を適切に実行）
    float corr_x = ax - accel_offset_x;
    float corr_y = ay - accel_offset_y;
    float corr_z = az - accel_offset_z;
    
    // 重力成分の除去：キャリブレーション時の静止状態から変化した分のみを取得
    // 静止状態（キャリブレーション時）を基準として、変化分のみを加速度とする
    data.accel_x = corr_x;
    data.accel_y = corr_y;
    data.accel_z = corr_z;
    
    // ジャイロデータは表示用のみ
    data.gyro_x = gx - gyro_offset_x;
    data.gyro_y = gy - gyro_offset_y;
    data.gyro_z = gz - gyro_offset_z;
    data.timestamp = millis();

    // --- 画面モード名・操作説明表示 ---
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);
    
    // 上部にモード名表示（背景をクリア）
    M5.Lcd.fillRect(0, 0, 240, 15, BLACK);
    M5.Lcd.setCursor(5, 5);
    const char* modeStr = "";
    if (display_mode == 0) modeStr = "通常グラフ";
    else modeStr = "加速度2次元";
    M5.Lcd.printf("[MODE] %s", modeStr);
    
    // 軸モード表示（2次元グラフ時のみ）
    if (display_mode == 1) {
        M5.Lcd.setCursor(150, 5);
        const char* axisStr = "";
        if (axis_mode == 0) axisStr = "XY軸";
        else if (axis_mode == 1) axisStr = "YZ軸";
        else axisStr = "XZ軸";
        M5.Lcd.printf("[軸:%s]", axisStr);
    }
    
    // 下部に操作説明表示（背景をクリア）
    M5.Lcd.fillRect(0, 150, 240, 15, BLACK);
    M5.Lcd.setCursor(5, 155);
    if (display_mode == 0) {
        M5.Lcd.print("A:画面切替  B長押:キャリブレーション");
    } else {
        M5.Lcd.print("A:画面切替  B:軸切替  B長押:軸リセット");
    }
    
    // 変位関連の計算を削除（不要になったため）

    if (display_mode == 0) {
        // 通常グラフ
        displayManager->showSwingGraph(data.accel_x, data.accel_y, data.accel_z);
        // センサーの生データも表示
        displayManager->showRawSensorData(ax, ay, az, gx, gy, gz);
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