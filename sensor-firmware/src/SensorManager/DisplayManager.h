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
    void showMessage(const std::string& msg);
    void showAccel2DGraph(float ax, float ay, float az, int axis_mode);
    void clear();
private:
    int x;
};
