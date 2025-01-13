#ifdef ESP8266
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif
#include <ModbusIP_ESP8266.h>

const int REG = 0;  // Modbus Hreg Offset
const int NUMBER_REG = 1;
const uint16_t RAW_MIN = 30994;
const uint16_t RAW_MAX = 34982;
const float PRESSURE_MIN = 0.0;    // kPa
const float PRESSURE_MAX = 50.0;   // kPa

IPAddress remote(192, 168, 246, 252);  // Address of Modbus Slave device
ModbusIP mb;                         //ModbusIP object

void setup() {
  Serial.begin(9600);
  Serial.print("Connecting to wifi");
static IP
  WiFi.begin("Rey", "hehehe123");

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

uint16_t res;

void loop() {
  if (mb.isConnected(remote)) {  // Check if connection to Modbus Slave is established

    if (mb.readHreg(remote, REG, &res, NUMBER_REG, NULL, 1)) {
      float pressure = mapPressure(res, RAW_MIN, RAW_MAX, PRESSURE_MIN, PRESSURE_MAX);
      Serial.println("Success reading");
      Serial.println(res);
      Serial.println(pressure);
    } else {
      Serial.println("Failed reading");
    }
    delay(1000);  // Pulling interval
  } else {
    Serial.println("Connecting to modbus");
    mb.connect(remote);  // Try to connect if no connection
    delay(100);          // Pulling interval
  }
  mb.task();  // Common local Modbus task
}

float mapPressure(uint16_t value, uint16_t rawMin, uint16_t rawMax, float pressureMin, float pressureMax) {
    Serial.print("Value received: ");
    Serial.println(value);
    
    if (value < rawMin) {
        Serial.println("Value below RAW_MIN!");
        value = rawMin;
    }
    if (value > rawMax) {
        Serial.println("Value above RAW_MAX!");
        value = rawMax;
    }
    
    float numerator = (float)(value - rawMin);
    float denominator = (float)(rawMax - rawMin);
    float ratio = numerator / denominator;
    float result = pressureMin + ratio * (pressureMax - pressureMin);
    
    Serial.print("Calculation steps: ");
    Serial.print("Numerator: "); Serial.println(numerator);
    Serial.print("Denominator: "); Serial.println(denominator);
    Serial.print("Ratio: "); Serial.println(ratio);
    
    return result;
}