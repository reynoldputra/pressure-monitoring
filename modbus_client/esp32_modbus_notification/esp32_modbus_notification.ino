#ifdef ESP8266
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif

#include <WiFiClientSecure.h>
#include <ModbusIP_ESP8266.h>
#include <UniversalTelegramBot.h>
#include <ArduinoJson.h>

// Telegram configuration
#define BOTtoken "7594584104:AAG-COojfNwNe5APYXN3vLYy7qJ00G63dUY"
#define CHAT_ID "-1002414792856"

// Zone configuration struct
struct ZoneConfig {
  String name;
  IPAddress ip;
  uint16_t reg;
  uint16_t numReg;
  uint8_t unitId;
  int maxThreshold;
  int minThreshold;
  boolean isAboveMax;
  boolean isBelowMin;
  unsigned long lastNotifTime;
};

struct ZoneNotification {
  String name;
  uint16_t pres_value;
  bool isMaxWarning;
  int maxThreshold;
  int minThreshold;
};

// Define zones - you can add more zones here
ZoneConfig zones[] = {
  {
    "Zone A",
    IPAddress(192,168,246,242),
    0,    // reg
    1,    // numReg
    1,    // unitId
    15,   // maxThreshold
    5,    // minThreshold
    false,// isAboveMax
    false,// isBelowMin
    0     // lastNotifTime
  }
  // Add more zones as needed
};

const int NUM_ZONES = sizeof(zones) / sizeof(zones[0]);
const unsigned long notifInterval = 5 * 1000;  // 5 seconds notification interval

WiFiClientSecure client;
UniversalTelegramBot bot(BOTtoken, client);
ModbusIP mb;

void sendMessageMultipleZones(ZoneNotification notifications[], int numZones) {
  String message = "[PRESSURE NOTIFICATION SUMMARY]\n\n";

  for (int i = 0; i < numZones; i++) {
    String zoneName = notifications[i].name;
    int pres_value = notifications[i].pres_value;
    bool isMaxWarning = notifications[i].isMaxWarning;
    int maxThresh = notifications[i].maxThreshold;
    int minThresh = notifications[i].minThreshold;

    message += "- " + zoneName + ":\n";
    message += "  Current: " + String(pres_value) + " Pa\n";
    message += "  Thresholds: Min " + String(minThresh) + " Pa, Max " + String(maxThresh) + " Pa\n";
    message += "  Status: ";
    
    if (isMaxWarning) {
      message += "ALERT - Above Maximum Threshold\n";
    } else {
      message += "WARNING - Below Minimum Threshold\n";
    }
    message += "\n";
  }

  message += "Please review the affected zones and take necessary actions.";

  bot.sendMessage(CHAT_ID, message, "");
  Serial.println(message);
}

void checkZoneThresholds(ZoneConfig& zone, uint16_t value) {
  unsigned long currentMillis = millis();
  bool shouldNotify = false;
  ZoneNotification notification = { 
    zone.name, 
    value, 
    false,
    zone.maxThreshold,
    zone.minThreshold 
  };

  // Check maximum threshold
  if (value >= zone.maxThreshold) {
    if (!zone.isAboveMax || (currentMillis - zone.lastNotifTime >= notifInterval)) {
      notification.isMaxWarning = true;
      shouldNotify = true;
      zone.isAboveMax = true;
      zone.lastNotifTime = currentMillis;
    }
  } else {
    zone.isAboveMax = false;
  }

  // Check minimum threshold
  if (value <= zone.minThreshold) {
    if (!zone.isBelowMin || (currentMillis - zone.lastNotifTime >= notifInterval)) {
      notification.isMaxWarning = false;
      shouldNotify = true;
      zone.isBelowMin = true;
      zone.lastNotifTime = currentMillis;
    }
  } else {
    zone.isBelowMin = false;
  }

  if (shouldNotify) {
    ZoneNotification notifications[] = { notification };
    sendMessageMultipleZones(notifications, 1);
  }
}

void setup() {
  Serial.begin(9600);
  Serial.print("Connecting to WiFi");

  client.setCACert(TELEGRAM_CERTIFICATE_ROOT);
  WiFi.begin("Rey", "hehehe123");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  bot.sendMessage(CHAT_ID, "Multi-Zone Monitoring Bot Connected!", "");

  mb.client();
}

void loop() {
  for (int i = 0; i < NUM_ZONES; i++) {
    if (mb.isConnected(zones[i].ip)) {
      uint16_t result;
      if (mb.readHreg(zones[i].ip, zones[i].reg, &result, zones[i].numReg, NULL, zones[i].unitId)) {
        Serial.print(zones[i].name + " reading: ");
        Serial.println(result);
        
        if (result != 0) {
          checkZoneThresholds(zones[i], result);
        }
      } else {
        Serial.println("Failed reading " + zones[i].name);
      }
    } else {
      Serial.println("Connecting to " + zones[i].name + " Modbus");
      mb.connect(zones[i].ip);
      delay(100);
    }
    delay(1000);  // Delay between reading different zones
  }

  mb.task();  // Common local Modbus task
}