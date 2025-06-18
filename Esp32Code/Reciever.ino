#include <esp_now.h>
#include <WiFi.h>
#include "RoboClaw.h"
#include <HardwareSerial.h>

#define ROBOCLAW_ADDR 0x80

HardwareSerial serial2(2);  // RX=16, TX=17
RoboClaw roboclaw(&serial2, 10000);
uint8_t receiverAddress[] = { 0xAC, 0x15, 0x18, 0xD8, 0xD0, 0xD8 };


typedef struct struct_message {
  int speed1;
  int speed2;
} struct_message;

typedef struct struct_message1 {
  int enc1;
  int enc2;
  float voltage;
  float speedL;
  float speedR;
} struct_message1;

struct_message1 sendingData;

struct_message incomingData;
const int ledPin = 2;
#define CPR 4000  // 1000 lines * 4 (quadrature)

void onDataRecv(const uint8_t *mac, const uint8_t *incomingDataRaw, int len) {
  memcpy(&incomingData, incomingDataRaw, sizeof(incomingData));

  Serial.printf("M1: %d, M2: %d\n", incomingData.speed1, incomingData.speed2);
  // digitalWrite(ledPin, !digitalRead(ledPin));

  if(incomingData.speed1 < 0){
    // roboclaw.BackwardM1(ROBOCLAW_ADDR, -incomingData.speed1);
    roboclaw.SpeedM1(ROBOCLAW_ADDR, incomingData.speed1);
  }else{
    // roboclaw.ForwardM1(ROBOCLAW_ADDR, incomingData.speed1);
    roboclaw.SpeedM1(ROBOCLAW_ADDR, incomingData.speed1);
  }
  if(incomingData.speed2 < 0){
    // roboclaw.BackwardM2(ROBOCLAW_ADDR, -incomingData.speed2);
    roboclaw.SpeedM2(ROBOCLAW_ADDR, incomingData.speed2);
  }else{
    // roboclaw.ForwardM2(ROBOCLAW_ADDR, incomingData.speed2);
    roboclaw.SpeedM2(ROBOCLAW_ADDR, incomingData.speed2);
  }

  if(incomingData.speed1 == 0){
    roboclaw.ForwardM1(ROBOCLAW_ADDR, 0);
    // roboclaw.BackwardM1(ROBOCLAW_ADDR, -incomingData.speed1);
    // roboclaw.SpeedM1(ROBOCLAW_ADDR, incomingData.speed1);
  }
  if(incomingData.speed2 == 0){
    // roboclaw.BackwardM1(ROBOCLAW_ADDR, -incomingData.speed1);
    roboclaw.ForwardM2(ROBOCLAW_ADDR, 0);
  }
  // roboclaw.ForwardM2(ROBOCLAW_ADDR, incomingData.speed2);
  // Read encoder values
  uint32_t enc1, enc2;
  bool valid1, valid2;
  enc1 = roboclaw.ReadEncM1(ROBOCLAW_ADDR, NULL, &valid1);
  enc2 = roboclaw.ReadEncM2(ROBOCLAW_ADDR, NULL, &valid2);

  bool valid3;
  uint16_t volts = roboclaw.ReadMainBatteryVoltage(ROBOCLAW_ADDR);

  struct_message1 telemetry;
  telemetry.enc1 = valid1 ? enc1 : -1;
  telemetry.enc2 = valid2 ? enc2 : -1;

  // Serial.print("Battery Voltage: ");
  // Serial.println(volts / 10.0);

  float x = volts/10.0;

  telemetry.voltage = x;

  bool valid4, valid5;
  int32_t speed1 = roboclaw.ReadSpeedM1(ROBOCLAW_ADDR,NULL, &valid4);  // counts/sec
  int32_t speed2 = roboclaw.ReadSpeedM2(ROBOCLAW_ADDR,NULL, &valid5);  // counts/sec

  telemetry.speedL = speed1;
  telemetry.speedR = speed2;

  

  // if (valid4 && valid5) {
  //   float rpm1 = speed1 * 60.0 / CPR;
  //   float rpm2 = speed2 * 60.0 / CPR;

  //   // Serial.print("Left Motor RPM: ");
  //   // Serial.print(rpm1);
  //   // Serial.print("\tRight Motor RPM: ");
  //   // Serial.println(rpm2);

  //   telemetry.speedL = rpm2;
  //   telemetry.speedR = rpm1;
  // } else {
  //   // Serial.println("⚠️ Invalid speed data");
  //   telemetry.speedL = -1;
  //   telemetry.speedR = -1;
  // }

  // Send back to sender
  esp_now_send(mac, (uint8_t *)&telemetry, sizeof(telemetry));
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  serial2.begin(38400, SERIAL_8N1, 16, 17);
  roboclaw.begin(38400);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, receiverAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add peer");
    return;
  }

  esp_now_register_recv_cb(onDataRecv);

  uint16_t volts = roboclaw.ReadMainBatteryVoltage(ROBOCLAW_ADDR);
  Serial.print("Battery Voltage: ");
  Serial.println(volts / 10.0);
}

void loop() {
  // Nothing
  // Serial.println("HHHELLJKLKJ");

  // uint32_t enc1, enc2;
  // bool valid1, valid2;
  // enc1 = roboclaw.ReadEncM1(ROBOCLAW_ADDR, NULL, &valid1);
  // enc2 = roboclaw.ReadEncM2(ROBOCLAW_ADDR, NULL, &valid2);

  // bool valid3;
  // uint16_t volts = roboclaw.ReadMainBatteryVoltage(ROBOCLAW_ADDR);

  // struct_message1 telemetry;
  // telemetry.enc1 = valid1 ? enc1 : -1;
  // telemetry.enc2 = valid2 ? enc2 : -1;

  // Serial.print("Battery Voltage: ");
  // Serial.println(volts / 10.0);

  // float x = volts/10.0;

  // telemetry.voltage = x;

  // bool valid4, valid5;
  // int32_t speed1 = roboclaw.ReadSpeedM1(ROBOCLAW_ADDR,NULL, &valid4);  // counts/sec
  // int32_t speed2 = roboclaw.ReadSpeedM2(ROBOCLAW_ADDR,NULL, &valid5);  // counts/sec

  // if (valid4 && valid5) {
  //   float rpm1 = speed1 * 60.0 / CPR;
  //   float rpm2 = speed2 * 60.0 / CPR;

  //   Serial.print("Left Motor RPM: ");
  //   Serial.print(rpm1);
  //   Serial.print("\tRight Motor RPM: ");
  //   Serial.println(rpm2);

  //   telemetry.speedL = rpm2;
  //   telemetry.speedR = rpm1;
  // } else {
  //   Serial.println("⚠️ Invalid speed data");
  //   telemetry.speedL = -1;
  //   telemetry.speedR = -1;
  // }
  
  // esp_now_send(receiverAddress, (uint8_t *)&telemetry, sizeof(telemetry));
  // delay(100);
}
