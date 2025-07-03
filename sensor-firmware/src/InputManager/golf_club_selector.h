#ifndef GOLF_CLUB_SELECTOR_H
#define GOLF_CLUB_SELECTOR_H

#include <Arduino.h>

#define CLUB_COUNT 8
#define PLAYER_COUNT 4

// Golf club types
enum ClubType {
    DRIVER = 0,
    IRON_3 = 1,
    IRON_5 = 2,
    IRON_7 = 3,
    IRON_9 = 4,
    PITCHING_WEDGE = 5,
    SAND_WEDGE = 6,
    PUTTER = 7
};

class GolfClubSelector {
private:
    int current_club_index;
    int current_player_index;
    unsigned long last_button_press;
    unsigned long button_debounce_time;
    
    void displayCurrentClub();
    void displayCurrentPlayer();

public:
    GolfClubSelector();
    
    // Initialize button handling
    bool initialize();
    
    // Update button states (call in main loop)
    void update();
    
    // Get current club selection
    ClubType getCurrentClub();
    String getCurrentClubName();
    
    // Get current player selection
    String getCurrentPlayerName();
};

#endif // GOLF_CLUB_SELECTOR_H