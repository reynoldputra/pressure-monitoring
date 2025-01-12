#ifdef ESP8266
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif
#include <ModbusIP_ESP8266.h>

int REG = 0;  // Modbus Hreg Offset
int NUMBER_REG = 8;

IPAddress remote(10, 10, 100, 254);  // Address of Modbus Slave device
ModbusIP mb;                         //ModbusIP object

void setup() {
  Serial.begin(9600);
  Serial.print("Connecting to wifi");

  WiFi.begin("HF2211_3A20", "");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  mb.client();
}

uint16_t res[8];

void loop() {
  if (mb.isConnected(remote)) {  // Check if connection to Modbus Slave is established

    if (mb.readHreg(remote, REG, res, NUMBER_REG, NULL, 1)) {
      Serial.println("Success reading");
      for (int j = 0; j < 8; j++) {
        Serial.print(res[j]);
        Serial.print(",");
      }
    } else {
      Serial.println("Failed reading");
    }

    Serial.println();
    delay(1000);  // Pulling interval
  } else {
    Serial.println("Connecting to modbus");
    mb.connect(remote);  // Try to connect if no connection
    delay(100);          // Pulling interval
  }
  mb.task();  // Common local Modbus task
}
