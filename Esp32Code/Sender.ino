#include <esp_now.h>
#include <WiFi.h>

typedef struct struct_message {
  int speed1;
  int speed2;
  bool solenoid1;
  bool solenoid2;
  bool solenoid3;
  bool solenoid4;
} struct_message;

typedef struct struct_message1 {
  int enc1;
  int enc2;
  float voltage;
  float speedL;
  float speedR;
} struct_message1;

struct_message outgoingData;
struct_message1 incomingData;

int MAX_POWER = 60000;
int MAX_TURN = 20000;

// CRSF buffer
uint8_t crsfBuffer[64];
int crsfPos = 0;

// Replace with your receiver’s MAC
uint8_t receiverAddress[] = { 0x88, 0x13, 0xBF, 0x62, 0xFC, 0x18 };

void setup() {
  Serial.begin(115200);
  Serial1.begin(420000, SERIAL_8N1, 22, 23); // CRSF UART

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

  // esp_now_register_send_cb(onDataSent);

  esp_now_register_recv_cb(onDataRecv);
}

void loop() {
  // while (Serial1.available()) {
  //   uint8_t byte = Serial1.read();

  //   if (crsfPos == 0 && byte != 0xC8) continue;

  //   crsfBuffer[crsfPos++] = byte;

  //   if (crsfPos > 2 && crsfPos >= crsfBuffer[1] + 2) {
  //     parseCRSFPacket(crsfBuffer, crsfPos);
  //     crsfPos = 0;
  //   }
  // }
  // delay(100);
}

void parseCRSFPacket(uint8_t *data, int len) {
  if (data[2] == 0x16) { // RC Channels frame
    uint16_t channels[16];
    uint8_t *p = &data[3];

    channels[0] = ((p[0] | p[1] << 8) & 0x07FF);
    channels[1] = ((p[1] >> 3 | p[2] << 5) & 0x07FF);
    channels[2] = ((p[2] >> 6 | p[3] << 2 | p[4] << 10) & 0x07FF);
    channels[3] = ((p[4] >> 1 | p[5] << 7) & 0x07FF);
    channels[4] = ((p[5] >> 4 | p[6] << 4) & 0x07FF);
    channels[5] = ((p[6] >> 7 | p[7] << 1 | p[8] << 9) & 0x07FF);
    channels[6] = ((p[8] >> 2 | p[9] << 6) & 0x07FF);
    channels[7] = ((p[9] >> 5 | p[10] << 3) & 0x07FF);
    channels[8]  = ((p[11] | p[12] << 8) & 0x07FF);
    channels[9]  = ((p[12] >> 3 | p[13] << 5) & 0x07FF);
    channels[10] = ((p[13] >> 6 | p[14] << 2 | p[15] << 10) & 0x07FF);


    float ch1 = ((channels[1] - 992.0f) / 820.0f); // Throttle
    float ch2 = ((channels[3] - 992.0f) / 820.0f); // Steering

    // Clamp values to -1.0 to 1.0
    ch1 = constrain(ch1, -1.0f, 1.0f);
    ch2 = constrain(ch2, -1.0f, 1.0f);

    // Optionally: Apply deadzone
    float deadzone = 0.05;
    if (fabs(ch1) < deadzone) ch1 = 0;
    if (fabs(ch2) < deadzone) ch2 = 0;

    float forward = ch1 * MAX_POWER;
    float turn = ch2 * MAX_POWER;

    int leftPower = forward + turn;
    int rightPower = forward - turn;

    Serial.printf("Sent -> L: %d, R: %d\n", leftPower, rightPower);

    // Read CH6 as digital switch
    // Serial.println(channels[6]);
    // Serial.println(channels[7]);
    // bool estopActivated = false;
    if (channels[6] > 1500) {  // Or adjust threshold as needed
      Serial.println("Active 1");
      // estopActivated = true;
      outgoingData.solenoid1 = true;
    } else {
      Serial.println("NOT ACTIVE 1");
      outgoingData.solenoid1 = false;
      // estopActivated = false;
    }
    if (channels[7] > 1500) {  // Or adjust threshold as needed
      Serial.println("Active 2");
      outgoingData.solenoid2 = true;
      // estopActivated = true;
    } else {
      Serial.println("NOT ACTIVE 2");
      outgoingData.solenoid2 = false;
      // estopActivated = false;
    }
    if (channels[8] > 1500) {  // Or adjust threshold as needed
      Serial.println("Active 3");
      outgoingData.solenoid3 = true;
      // estopActivated = true;
    } else {
      Serial.println("NOT ACTIVE 3");
      outgoingData.solenoid3 = false;
      // estopActivated = false;
    }
    if (channels[9] > 1500) {  // Or adjust threshold as needed
      Serial.println("Active 4");
      outgoingData.solenoid4 = true;
      // estopActivated = true;
    } else {
      Serial.println("NOT ACTIVE 4");
      outgoingData.solenoid4 = false;
      // estopActivated = false;
    }
  }
}

void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("Send Status: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Success" : "Fail");
}

void onDataRecv(const uint8_t *mac, const uint8_t *incomingData, int len) {
  struct_message1 encData;
  memcpy(&encData, incomingData, sizeof(encData));
  Serial.printf("ENCODER,%d,%d\n", encData.enc1, encData.enc2);
  Serial.printf("VOLTAGE,%.2f\n", encData.voltage);
  Serial.printf("SPEED,%.2f,%.2f\n", encData.speedL, encData.speedR);
}

