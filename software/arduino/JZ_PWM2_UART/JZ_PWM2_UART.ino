// Пример для плат Arduino с отдельным аппаратным UART.
// На Arduino Uno аппаратный Serial занят USB; для стенда можно применить SoftwareSerial.

#define PWM_SERIAL Serial1

void sendCommand(const char* command) {
  PWM_SERIAL.print(command);
  Serial.print("TX: ");
  Serial.println(command);

  unsigned long deadline = millis() + 1000;
  while (millis() < deadline) {
    if (PWM_SERIAL.available()) {
      String reply = PWM_SERIAL.readStringUntil('\n');
      reply.trim();
      Serial.print("RX: ");
      Serial.println(reply);
      return;
    }
  }
  Serial.println("RX timeout");
}

void setup() {
  Serial.begin(115200);
  PWM_SERIAL.begin(9600);
  delay(500);

  sendCommand("S1F100T");
  sendCommand("S1D025T");
  sendCommand("S2F25.0T");
  sendCommand("S2D075T");
}

void loop() {}
