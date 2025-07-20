#include <M5StickCPlus2.h>
#include "../src/SensorManager/imu_data_acquisition.h"
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <FS.h>
#include <SPIFFS.h>

IMUDataAcquisition imu_sensor;

// WiFi設定
#include "wifi_config.h" // WiFi情報を別ファイルに分離
WebServer server(80);

// CSV保存関数
void saveIMUDataToCSV(const SwingData &data)
{
    bool writeHeader = !SPIFFS.exists("/imu_log.csv");
    File file = SPIFFS.open("/imu_log.csv", FILE_APPEND);
    if (!file)
    {
        M5.Lcd.setCursor(10, 50);
        M5.Lcd.setTextColor(RED, BLACK);
        M5.Lcd.println("CSV open failed!");
        return;
    }
    if (writeHeader)
    {
        file.println("timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z");
    }
    file.printf("%lu,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f\n",
                data.timestamp, data.accel_x, data.accel_y, data.accel_z,
                data.gyro_x, data.gyro_y, data.gyro_z);
    file.close();
}

// MIMEタイプ推定
String getContentType(String filename)
{
    if (server.hasArg("download"))
        return "application/octet-stream";
    else if (filename.endsWith(".csv"))
        return "text/csv";
    else if (filename.endsWith(".htm"))
        return "text/html";
    else if (filename.endsWith(".html"))
        return "text/html";
    else if (filename.endsWith(".css"))
        return "text/css";
    else if (filename.endsWith(".js"))
        return "application/javascript";
    else if (filename.endsWith(".png"))
        return "image/png";
    else if (filename.endsWith(".gif"))
        return "image/gif";
    else if (filename.endsWith(".jpg"))
        return "image/jpeg";
    else if (filename.endsWith(".ico"))
        return "image/x-icon";
    else if (filename.endsWith(".xml"))
        return "text/xml";
    else if (filename.endsWith(".pdf"))
        return "application/x-pdf";
    else if (filename.endsWith(".zip"))
        return "application/x-zip";
    else if (filename.endsWith(".gz"))
        return "application/x-gzip";
    return "text/plain";
}

// ファイル送信
bool handleFileRead(String path)
{
    if (SPIFFS.exists(path))
    {
        File file = SPIFFS.open(path, "r");
        server.streamFile(file, getContentType(path));
        file.close();
        return true;
    }
    server.send(404, "text/plain", "File not found");
    return false;
}

void handleNotFound()
{
    if (!handleFileRead(server.uri()))
    {
        server.send(404, "text/plain", "File not found");
    }
}

void setup()
{
    M5.begin();
    M5.Lcd.setRotation(3);
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.setTextSize(1);

    if (!SPIFFS.begin(true))
    { // trueで自動フォーマット
        M5.Lcd.println("SPIFFS Init Failed!");
        while (1)
            delay(1000);
    }

    // 起動時にCSVファイルを削除（毎回新規作成）
    if (SPIFFS.exists("/imu_log.csv"))
    {
        SPIFFS.remove("/imu_log.csv");
    }

    if (!imu_sensor.initialize())
    {
        M5.Lcd.setCursor(10, 30);
        M5.Lcd.println("IMU Init Failed!");
        while (1)
            delay(1000);
    }
    M5.Lcd.setCursor(10, 10);
    M5.Lcd.println("Golf HILS Sensor");

    // WiFi接続
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        M5.Lcd.print(".");
    }
    M5.Lcd.setCursor(10, 30);
    M5.Lcd.println("WiFi Connected!");
    M5.Lcd.println(WiFi.localIP());

    if (MDNS.begin("esp32"))
    {
        M5.Lcd.println("MDNS responder started");
    }

    server.onNotFound(handleNotFound);
    server.begin();
}

void loop()
{
    SwingData data = imu_sensor.readSwingData();
    saveIMUDataToCSV(data);
    server.handleClient();
    delay(20);
}
