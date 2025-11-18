// SCANNER FELITRON COMO SERIAL KEYBOARD TRIGGER

const int rowPins[4] = {D1, D2, D5, D6};
const int colPins[4] = {D7, D0, D3, D4};

char keymap[4][4] = {
  {'1','2','3','M'},
  {'5','6','7','4'},
  {'9','0','*','8'},
  {'A','B','C','#'}
};

bool lastState[4][4];

void setup() {
  Serial.begin(115200);

  for (int r = 0; r < 4; r++) {
    pinMode(rowPins[r], OUTPUT);
    digitalWrite(rowPins[r], HIGH);
  }

  for (int c = 0; c < 4; c++) {
    pinMode(colPins[c], INPUT_PULLUP);
  }

  memset(lastState, 0, sizeof(lastState));
}

void loop() {
  for (int r=0; r<4; r++) {
    for (int rr=0; rr<4; rr++)
      digitalWrite(rowPins[rr], rr == r ? LOW : HIGH);

    delayMicroseconds(40);

    for (int c=0; c<4; c++) {
      bool pressed = (digitalRead(colPins[c]) == LOW);

      if (pressed && !lastState[r][c]) {
        char k = keymap[r][c];
        Serial.print("KEY_");
        Serial.println(k);   // ← ENVIA PRO PC
      }

      lastState[r][c] = pressed;
    }
  }

  delay(10);
}
