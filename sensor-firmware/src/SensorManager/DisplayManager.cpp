#include "DisplayManager.h"

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

DisplayManager::DisplayManager() : x(0) {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);
}

void DisplayManager::showSwingGraph(float ax, float ay, float az) {
    int y0 = 40, y_scale = 20;
    if (x == 0) {
        M5.Lcd.fillRect(0, y0 - 30, 240, 60, BLACK);
    }
    int ax_y = y0 - (int)(ax * y_scale);
    int ay_y = y0 - (int)(ay * y_scale);
    int az_y = y0 - (int)(az * y_scale);
    if (ax_y < 0) ax_y = 0; if (ax_y > 79) ax_y = 79;
    if (ay_y < 0) ay_y = 0; if (ay_y > 79) ay_y = 79;
    if (az_y < 0) az_y = 0; if (az_y > 79) az_y = 79;

    M5.Lcd.drawPixel(x, ax_y, RED);
    M5.Lcd.drawPixel(x, ay_y, GREEN);
    M5.Lcd.drawPixel(x, az_y, BLUE);

    x++;
    if (x >= 240) x = 0;

    M5.Lcd.setCursor(0, 0);
    M5.Lcd.printf("ax:%.2f ay:%.2f az:%.2f", ax, ay, az);
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
    int cx = 120, cy = 80; // 画面中心（中央付近）
    int scale = 40; // 拡大倍率
    int gx, gy;
    uint16_t color = RED;
    float z_centered = az - 1.0; // z軸は重力分補正
    switch(axis_mode) {
        case 0: // xy
            gx = cx + (int)(ax * scale);
            gy = cy - (int)(ay * scale);
            color = GREEN;
            break;
        case 1: // yz
            gx = cx + (int)(ay * scale);
            gy = cy - (int)(z_centered * scale);
            color = BLUE;
            break;
        case 2: // xz
            gx = cx + (int)(ax * scale);
            gy = cy - (int)(z_centered * scale);
            color = YELLOW;
            break;
    }
    // 背景・軸描画
    M5.Lcd.fillRect(cx-60, cy-60, 120, 120, BLACK);
    M5.Lcd.drawLine(cx-60, cy, cx+60, cy, WHITE); // x軸
    M5.Lcd.drawLine(cx, cy-60, cx, cy+60, WHITE); // y軸
    // 軸ラベル
    M5.Lcd.setTextColor(WHITE, BLACK);
    switch(axis_mode) {
        case 0:
            M5.Lcd.setCursor(cx+65, cy-10); M5.Lcd.print("X");
            M5.Lcd.setCursor(cx-10, cy-65); M5.Lcd.print("Y");
            break;
        case 1:
            M5.Lcd.setCursor(cx+65, cy-10); M5.Lcd.print("Y");
            M5.Lcd.setCursor(cx-10, cy-65); M5.Lcd.print("Z");
            break;
        case 2:
            M5.Lcd.setCursor(cx+65, cy-10); M5.Lcd.print("X");
            M5.Lcd.setCursor(cx-10, cy-65); M5.Lcd.print("Z");
            break;
    }
    // 点描画
    M5.Lcd.fillCircle(gx, gy, 4, color);
    // 数値表示
    M5.Lcd.setCursor(10, 10);
    switch(axis_mode) {
        case 0:
            M5.Lcd.printf("Accel XY: x=%.2f y=%.2f", ax, ay);
            break;
        case 1:
            M5.Lcd.printf("Accel YZ: y=%.2f z=%.2f", ay, z_centered);
            break;
        case 2:
            M5.Lcd.printf("Accel XZ: x=%.2f z=%.2f", ax, z_centered);
            break;
    }
}

void DisplayManager::clear() {
    M5.Lcd.fillScreen(BLACK);
}
