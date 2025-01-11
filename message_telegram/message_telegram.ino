// /*
//  *  This sketch demonstrates how to scan WiFi networks.
//  *  The API is based on the Arduino WiFi Shield library, but has significant changes as newer WiFi functions are supported.
//  *  E.g. the return value of `encryptionType()` different because more modern encryption is supported.
//  */
// #include <WiFi.h>
// #include <WifiClientSecure.h>
// #include <UniversalTelegramBot.h>
// #include <ArduinoJson.h>

// //Replace with your network credentials
// const char* ssid = "5027211055@student.its.ac.id";
// const char* password = "Yupienzo97";

// //Initial Telegram BOT
// #define BOTtoken "7594584104:AAG-COojfNwNe5APYXN3vLYy7qJ00G63dUY"
// #define CHAT_ID "1125451663"

// WifiClientSecure client;
// UniversalTelegramBot bot(BOTtoken, client);

// const int motionSensor = 14;
// bool motionDetected = false;

// void setup(){
//   Serial.begin(115200);

//   client.setCACert(TELEGRAM_CERTIFICATE_ROOT);

//   pinMode(motionSensor, INPUT_PULLUP);

//   attachInterrupt(digitalPinToInterrupt(motionSensor), detectsMovement, RISINg);

//   Serial.print("Connecting Wifi: ");
//   Serial.println(ssid);

//   Wifi.mode(WIFI_STA);
//   Wifi.begin(ssid, password);

//   while (WiFi.status() != WL_CONNECTED){
//     Serial.print(".");
//     delay(500);
//   }

//   Serial.println("");
//   Serial.println("WiFi connected");
//   Serial.print("IP address: ");
//   Serial.println(WiFi.localIP());

//   bot.sendMessage(CHAT_ID, "Bot started up", "");
// }

// void loop(){
//   if(motionDetected){
//     bot.sendMessage(CHAT_ID, "Tekanan Melebihi Maksimum!", "");
//     Serial.println("Tekanan melebihi");
//     motionDetected = false;
//   }
// }


#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>
#include <ArduinoJson.h>

const char* ssid = "DESKTOP-TAF1LRF 9416";
const char* password = "97979797";

#define BOTtoken "7594584104:AAG-COojfNwNe5APYXN3vLYy7qJ00G63dUY"
#define CHAT_ID "-1002414792856" 

WiFiClientSecure client;
UniversalTelegramBot bot(BOTtoken, client);

bool isSendMessageEnabled = false; // Variabel untuk menghindari bentrok dengan nama fungsi

void sendMessage(bool isMaxWarning) {
  if (isMaxWarning) {
    bot.sendMessage(CHAT_ID, "[PERINGATAN]\n\nTekanan mencapai MAXIMUM 20pA, segera lakukan tindakan!", "");
    Serial.println("[PERINGATAN]\n\nTekanan mencapai MAXIMUM 20pA, segera lakukan tindakan!");
  } else {
    bot.sendMessage(CHAT_ID, "[PERINGATAN]\n\nTekanan berada pada MINIMUM 15pA, segera lakukan tindakan!", "");
    Serial.println("[PERINGATAN]\n\nTekanan berada pada MINIMUM 15pA, segera lakukan tindakan!");
  }
}

void setup() {
  Serial.begin(115200);

  client.setCACert(TELEGRAM_CERTIFICATE_ROOT);

  Serial.print("Menghubungkan ke WiFi: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.println("");
  Serial.println("WiFi terhubung!");
  Serial.print("Alamat IP: ");
  Serial.println(WiFi.localIP());

  bot.sendMessage(CHAT_ID, "Bot Notifikasi terhubung!", "");

  bool isMaxWarning = true;
  sendMessage(isMaxWarning); // Panggil fungsi
  isMaxWarning = !isMaxWarning;
  delay(10000);
  sendMessage(false);
  // sendMessage(!isMaxWarning)
}

void loop() {
  // Biarkan kosong jika tidak ada logika yang perlu dijalankan terus-menerus
}


// void loop() {
//   // Simulasi pengiriman pesan setiap 10 detik
//   static unsigned long lastTime = 0;
//   unsigned long currentTime = millis();
//   static bool isMaxWarning = true; 

//   if (currentTime - lastTime > 10000) { // 10 detik
//     lastTime = currentTime;
//     if (isMaxWarning) {
//       bot.sendMessage(CHAT_ID, "[PERINGATAN]\n\nTekanan mencapai MAXIMUM 20pA, segera lakukan tindakan!", "");
//       Serial.println("[PERINGATAN]\n\nTekanan mencapai MAXIMUM 20pA, segera lakukan tindakan!");
//     } else {
//       bot.sendMessage(CHAT_ID, "[PERINGATAN]\n\nTekanan mencapai berada pada MINIMUM 15pA, segera lakukan tindakan!", "");
//       Serial.println("[PERINGATAN]\n\nTekanan mencapai berada pada MINIMUM 15pA, segera lakukan tindakan!");
//     }

//     isMaxWarning = !isMaxWarning;
//   }
// }
