#ifdef ESP8266
 #include <ESP8266WiFi.h>
#else
 #include <WiFi.h>
#endif
#include <ModbusIP_ESP8266.h>

int REG = 0;               // Modbus Hreg Offset
int NUMBER_REG = 8;
IPAddress remote(192, 168, 246, 242);  // Address of Modbus Slave device

ModbusIP mb;  //ModbusIP object

void setup() {
  Serial.begin(9600);
  Serial.print("Connecting to wifi");
 
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

uint16_t res[8];

void loop() {
  if (mb.isConnected(remote)) {   // Check if connection to Modbus Slave is established
    Serial.println("Success reading");
    mb.readHreg(remote, REG, res, NUMBER_REG);  // Initiate Read Coil from Modbus Slave
        for (int j = 0; j < 5; j++) {
      Serial.print(res[j]);
      Serial.print(",");
    }   
    Serial.println();
      delay(1000);                     // Pulling interval
  } else {
    Serial.println("Connecting to modbus");
    mb.connect(remote);           // Try to connect if no connection
      delay(100);                     // Pulling interval
  }
  mb.task();                      // Common local Modbus task

}