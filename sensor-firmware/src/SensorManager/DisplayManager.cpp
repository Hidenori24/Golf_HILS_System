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

void DisplayManager::clear() {
    M5.Lcd.fillScreen(BLACK);
}
