// 変位2次元グラフ描画
#include "DisplayManager.h"
#include <M5Unified.h>
#ifndef RED
#define RED     0xF800
#endif
#ifndef GREEN
#define GREEN   0x07E0
#endif
#ifndef BLUE
#define BLUE    0x001F
#endif
#ifndef YELLOW
#define YELLOW  0xFFE0
#endif
#ifndef WHITE
#define WHITE   0xFFFF
#endif
#ifndef BLACK
#define BLACK   0x0000
#endif

void DisplayManager::showDisplacement2DGraph(float px, float py, float pz, int axis_mode) {
    int cx = 120, cy = 90; // 画面中心を下に移動
    int scale = 40; // 拡大倍率（調整可）
    int gx, gy;
    uint16_t color = RED;
    
    // 範囲制限
    if (gx < 0) gx = 0; if (gx > 240) gx = 240;
    if (gy < 30) gy = 30; if (gy > 135) gy = 135;
    
    switch(axis_mode) {
        case 0: // xy
            gx = cx + (int)(px * scale);
            gy = cy - (int)(py * scale);
            color = GREEN;
            break;
        case 1: // yz
            gx = cx + (int)(py * scale);
            gy = cy - (int)(pz * scale);
            color = BLUE;
            break;
        case 2: // xz
            gx = cx + (int)(px * scale);
            gy = cy - (int)(pz * scale);
            color = YELLOW;
            break;
    }
    
    // 範囲制限（再計算後）
    if (gx < 60) gx = 60; if (gx > 180) gx = 180;
    if (gy < 30) gy = 30; if (gy > 135) gy = 135;
    
    // 背景・軸描画
    M5.Lcd.fillRect(cx-60, cy-45, 120, 90, BLACK);
    M5.Lcd.drawLine(cx-60, cy, cx+60, cy, WHITE); // x軸
    M5.Lcd.drawLine(cx, cy-45, cx, cy+45, WHITE); // y軸
    
    // 軸ラベル（位置を調整）
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);
    switch(axis_mode) {
        case 0:
            M5.Lcd.setCursor(cx+50, cy+5); M5.Lcd.print("X");
            M5.Lcd.setCursor(cx+5, cy-40); M5.Lcd.print("Y");
            break;
        case 1:
            M5.Lcd.setCursor(cx+50, cy+5); M5.Lcd.print("Y");
            M5.Lcd.setCursor(cx+5, cy-40); M5.Lcd.print("Z");
            break;
        case 2:
            M5.Lcd.setCursor(cx+50, cy+5); M5.Lcd.print("X");
            M5.Lcd.setCursor(cx+5, cy-40); M5.Lcd.print("Z");
            break;
    }
    // 点描画
    M5.Lcd.fillCircle(gx, gy, 3, color);
}

DisplayManager::DisplayManager() : x(0) {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);
}

void DisplayManager::showSwingGraph(float ax, float ay, float az) {
    int y0 = 70, y_scale = 20; // グラフの中心位置を調整
    if (x == 0) {
        M5.Lcd.fillRect(0, y0 - 30, 240, 60, BLACK);
    }
    int ax_y = y0 - (int)(ax * y_scale);
    int ay_y = y0 - (int)(ay * y_scale);
    int az_y = y0 - (int)(az * y_scale);
    if (ax_y < 35) ax_y = 35; if (ax_y > 105) ax_y = 105;
    if (ay_y < 35) ay_y = 35; if (ay_y > 105) ay_y = 105;
    if (az_y < 35) az_y = 35; if (az_y > 105) az_y = 105;

    M5.Lcd.drawPixel(x, ax_y, RED);
    M5.Lcd.drawPixel(x, ay_y, GREEN);
    M5.Lcd.drawPixel(x, az_y, BLUE);

    x++;
    if (x >= 240) x = 0;

    // 下部に補正後の加速度を表示
    M5.Lcd.fillRect(0, 120, 240, 20, BLACK);
    M5.Lcd.setCursor(0, 125);
    M5.Lcd.printf("補正済(G): x=%.2f y=%.2f z=%.2f", ax, ay, az);
}

void DisplayManager::showRawSensorData(float raw_ax, float raw_ay, float raw_az, float raw_gx, float raw_gy, float raw_gz) {
    // センサー生データを画面上部に表示
    M5.Lcd.fillRect(0, 10, 240, 20, BLACK);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);
    
    M5.Lcd.setCursor(0, 12);
    M5.Lcd.printf("生加速度(G): x=%.2f y=%.2f z=%.2f", raw_ax, raw_ay, raw_az);
    
    M5.Lcd.setCursor(0, 22);
    M5.Lcd.printf("ジャイロ(dps): x=%.1f y=%.1f z=%.1f", raw_gx, raw_gy, raw_gz);
}

void DisplayManager::showMessage(const std::string& msg) {
    M5.Lcd.setCursor(40, 30);
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(YELLOW, BLACK);
    M5.Lcd.printf("%s", msg.c_str());
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(WHITE, BLACK);
}

// axis_mode: 0=xy, 1=yz, 2=xz
void DisplayManager::showAccel2DGraph(float ax, float ay, float az, int axis_mode) {
    int cx = 120, cy = 90; // 画面中心を下に移動
    int scale = 40; // 拡大倍率
    int gx, gy;
    uint16_t color = RED;
    // z軸の重力補正は不要（キャリブレーション時に処理済み）
    switch(axis_mode) {
        case 0: // xy
            gx = cx + (int)(ax * scale);
            gy = cy - (int)(ay * scale);
            color = GREEN;
            break;
        case 1: // yz
            gx = cx + (int)(ay * scale);
            gy = cy - (int)(az * scale);
            color = BLUE;
            break;
        case 2: // xz
            gx = cx + (int)(ax * scale);
            gy = cy - (int)(az * scale);
            color = YELLOW;
            break;
    }
    
    // 範囲制限
    if (gx < 60) gx = 60; if (gx > 180) gx = 180;
    if (gy < 30) gy = 30; if (gy > 135) gy = 135;
    
    // 背景・軸描画
    M5.Lcd.fillRect(cx-60, cy-45, 120, 90, BLACK);
    M5.Lcd.drawLine(cx-60, cy, cx+60, cy, WHITE); // x軸
    M5.Lcd.drawLine(cx, cy-45, cx, cy+45, WHITE); // y軸
    
    // 軸ラベル（位置を調整）
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);
    switch(axis_mode) {
        case 0:
            M5.Lcd.setCursor(cx+50, cy+5); M5.Lcd.print("X");
            M5.Lcd.setCursor(cx+5, cy-40); M5.Lcd.print("Y");
            break;
        case 1:
            M5.Lcd.setCursor(cx+50, cy+5); M5.Lcd.print("Y");
            M5.Lcd.setCursor(cx+5, cy-40); M5.Lcd.print("Z");
            break;
        case 2:
            M5.Lcd.setCursor(cx+50, cy+5); M5.Lcd.print("X");
            M5.Lcd.setCursor(cx+5, cy-40); M5.Lcd.print("Z");
            break;
    }
    // 点描画
    M5.Lcd.fillCircle(gx, gy, 3, color);
}

void DisplayManager::clear() {
    M5.Lcd.fillScreen(BLACK);
}
