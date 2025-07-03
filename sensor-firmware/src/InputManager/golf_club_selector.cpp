#include "golf_club_selector.h"
#include <M5StickCPlus2.h>

GolfClubSelector::GolfClubSelector() {
    current_club_index = 0;
    last_button_press = 0;
    button_debounce_time = 200; // 200ms debounce
}

bool GolfClubSelector::initialize() {
    // M5StickC Plus2 buttons are initialized with M5.begin()
    displayCurrentClub();
    return true;
}

void GolfClubSelector::update() {
    // Check button A for club selection
    if (M5.BtnA.wasPressed()) {
        unsigned long current_time = millis();
        if (current_time - last_button_press > button_debounce_time) {
            current_club_index = (current_club_index + 1) % CLUB_COUNT;
            displayCurrentClub();
            last_button_press = current_time;
        }
    }
    
    // Check button B for player name cycling
    if (M5.BtnB.wasPressed()) {
        unsigned long current_time = millis();
        if (current_time - last_button_press > button_debounce_time) {
            current_player_index = (current_player_index + 1) % PLAYER_COUNT;
            displayCurrentPlayer();
            last_button_press = current_time;
        }
    }
}

ClubType GolfClubSelector::getCurrentClub() {
    return static_cast<ClubType>(current_club_index);
}

String GolfClubSelector::getCurrentClubName() {
    switch(getCurrentClub()) {
        case DRIVER: return "Driver";
        case IRON_3: return "3-Iron";
        case IRON_5: return "5-Iron";
        case IRON_7: return "7-Iron";
        case IRON_9: return "9-Iron";
        case PITCHING_WEDGE: return "P-Wedge";
        case SAND_WEDGE: return "S-Wedge";
        case PUTTER: return "Putter";
        default: return "Unknown";
    }
}

String GolfClubSelector::getCurrentPlayerName() {
    const String players[PLAYER_COUNT] = {"Player1", "Player2", "Player3", "Guest"};
    return players[current_player_index];
}

void GolfClubSelector::displayCurrentClub() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE);
    M5.Lcd.setTextSize(2);
    M5.Lcd.setCursor(10, 30);
    M5.Lcd.println("Club:");
    M5.Lcd.setCursor(10, 50);
    M5.Lcd.println(getCurrentClubName());
    M5.Lcd.setTextSize(1);
    M5.Lcd.setCursor(10, 80);
    M5.Lcd.println("A: Next Club");
}

void GolfClubSelector::displayCurrentPlayer() {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE);
    M5.Lcd.setTextSize(2);
    M5.Lcd.setCursor(10, 30);
    M5.Lcd.println("Player:");
    M5.Lcd.setCursor(10, 50);
    M5.Lcd.println(getCurrentPlayerName());
    M5.Lcd.setTextSize(1);
    M5.Lcd.setCursor(10, 80);
    M5.Lcd.println("B: Next Player");
}