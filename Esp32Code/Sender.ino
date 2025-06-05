#include <esp_now.h>
#include <WiFi.h>

typedef struct struct_message {
  int speed1;
  int speed2;
} struct_message;

typedef struct struct_message1 {
  int enc1;
  int enc2;
  double voltage;
} struct_message1;

struct_message outgoingData;
struct_message1 incomingData;

// Replace with your receiver’s MAC
uint8_t receiverAddress[] = { 0x88, 0x13, 0xBF, 0x62, 0xFC, 0x18 };

void setup() {
  Serial.begin(115200);
  Serial1.begin(9600);

  WiFi.mode(WIFI_STA);
  Serial.print("ESP32 MAC Address: ");
  Serial.println(WiFi.macAddress());
  WiFi.disconnect();

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, receiverAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  // if (esp_now_add_peer(&peerInfo) != ESP_OK) {
  //   Serial.println("Failed to add peer");
  //   return;
  // }

  Serial.println("Trying to add peer...");
  bool connected = false;
  while (!connected) {
    if (esp_now_add_peer(&peerInfo) == ESP_OK) {
      Serial.println("✅ Peer added successfully");
      connected = true;
    } else {
      Serial.println("❌ Failed to add peer. Retrying...");
      delay(1000);  // Wait before retry
    }
  }

  esp_now_register_send_cb(onDataSent);

  esp_now_register_recv_cb(onDataRecv);
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    int comma = line.indexOf(',');

    if (comma > 0) {
      int s1 = line.substring(0, comma).toInt();
      int s2 = line.substring(comma + 1).toInt();

      outgoingData.speed1 = s1;
      outgoingData.speed2 = s2;

      esp_now_send(receiverAddress, (uint8_t *)&outgoingData, sizeof(outgoingData));
      Serial.printf("Sent -> M1: %d, M2: %d\n", s1, s2);
    }
  }
  // Serial1.println("HELLLOOO");
}

void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("Send Status: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Success" : "Fail");
}

void onDataRecv(const uint8_t *mac, const uint8_t *incomingData, int len) {
  struct_message1 encData;
  memcpy(&encData, incomingData, sizeof(encData));
  Serial.printf("ENCODER,%d,%d\n", encData.enc1, encData.enc2);
   Serial.printf("VOLTAGE,%d\n", encData.voltage);
}

