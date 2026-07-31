// ESP32: пример обмена через UART2.
// ВНИМАНИЕ: сначала измерьте уровень TXD модуля. При 5 В нужен делитель/level shifter.

HardwareSerial PwmSerial(2);

constexpr int RX_PIN = 16;  // ESP32 RX <- JZ-PWM2 TXD
constexpr int TX_PIN = 17;  // ESP32 TX -> JZ-PWM2 RXD

bool sendCommand(const char* command) {
  while (PwmSerial.available()) PwmSerial.read();
  PwmSerial.print(command);
  PwmSerial.flush();

  String reply;
  const unsigned long deadline = millis() + 1000;
  while (millis() < deadline) {
    while (PwmSerial.available()) {
      char c = static_cast<char>(PwmSerial.read());
      if (c == '\r' || c == '\n') {
        if (reply.length() > 0) break;
      } else {
        reply += c;
      }
    }
    if (reply == "DOWN" || reply == "DONE") return true;
    if (reply == "FALL" || reply == "FAIL") return false;
    delay(1);
  }

  Serial.printf("Нет распознанного ответа на %s; принято: %s\n", command, reply.c_str());
  return false;
}

void setup() {
  Serial.begin(115200);
  PwmSerial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(500);

  sendCommand("S1F100T");
  sendCommand("S1D025T");
  sendCommand("S2F25.0T");
  sendCommand("S2D075T");
}

void loop() {}
