#pragma once
#include <M5Unified.h>
#include <string>

enum class DisplayMode {
    SwingGraph,
    Message
};

class DisplayManager {
public:
    DisplayManager();
    void showSwingGraph(float ax, float ay, float az);
    void showRawSensorData(float raw_ax, float raw_ay, float raw_az, float raw_gx, float raw_gy, float raw_gz);
    void showMessage(const std::string& msg);
    void showAccel2DGraph(float ax, float ay, float az, int axis_mode);
    void showDisplacement2DGraph(float px, float py, float pz, int axis_mode);
    void clear();
private:
    int x;
};
