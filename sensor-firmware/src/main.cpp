#include <M5StickCPlus2.h>
#include "../src/SensorManager/imu_data_acquisition.h"

IMUDataAcquisition imu_sensor;

void setup() {
    M5.begin();
    M5.Lcd.setRotation(3);
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);
    
    if (!imu_sensor.initialize()) {
        M5.Lcd.setCursor(10, 30);
        M5.Lcd.println("IMU Init Failed!");
        while(1) delay(1000);
    }
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.println("Golf HILS Sensor");
}

void loop() {
    SwingData data = imu_sensor.readSwingData();
    delay(20); // 適度な間隔で更新
}
