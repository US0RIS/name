/*
  SpinTrap controller - closed-loop rotor speed control for rotation-induced levitation.

  Hardware (see docs/PROTOTYPE.md):
    Arduino Nano (ATmega328P, 16 MHz)
    D9  -> ESC signal (standard 50 Hz servo PWM, 1000-2000 us)
    D2  <- Hall latch output (US1881 / TLE4945 / SS460S, open drain, 10k pull-up to 5V)
           mounted in the shroud wall at rotor-centre height; the rotor dipole gives exactly
           one rising edge per revolution, so f_edge = f_rotor.
    D4  <- push button to GND (start / land)
    D13 -> LED (on = speed locked within +-0.5 Hz)
    A0  <- optional 10k potentiometer (speed trim +-20 Hz around set point)

  Serial (115200 baud), one command per line:
    ARM            arm the ESC (sends minimum throttle for 3 s). Required once after power-up.
    S <hz>         go to <hz> with a soft ramp (default ramp rate 20 Hz/s)
    RATE <hz/s>    set ramp rate
    L              LAND: ramp to the release speed (LAND_HZ, default 150 Hz) and hold there.
                   The floater detaches and settles on the vessel floor.
                   Then lower the vessel at least 30 mm before stopping.
    X!             STOP (throttle to minimum).  Only do this after L + lowering the vessel:
                   at low speed the rotor acts as a static magnet and pulls the floater up.
    LANDHZ <hz>    set the release speed
    LOG <0|1>      stream "t_ms,setpoint_hz,measured_hz,throttle_us" at 20 Hz
    ?              status
  Button: short press while stopped -> ramp to DEFAULT_HZ; short press while running -> LAND.

  Safety: speed is limited to MAX_HZ; if the tachometer signal disappears while the throttle
  is above idle for >300 ms the throttle is cut (sensor fault or rotor jam).
*/
#include <Servo.h>

const float DEFAULT_HZ = 200.0;
const float MAX_HZ = 280.0;          // 16 800 rpm; check your motor/hub rating before raising
float LAND_HZ = 150.0;

const int PIN_ESC = 9, PIN_HALL = 2, PIN_BTN = 4, PIN_LED = 13, PIN_POT = A0;
const bool USE_POT = false;

Servo esc;
volatile unsigned long lastEdgeUs = 0, periodUs = 0;
volatile unsigned long edgeCount = 0;

float target = 0, setpoint = 0, rampRate = 20.0;   // Hz, Hz, Hz/s
float integ = 0;
// feed-forward: throttle_us ~ US0 + KFF * f  (auto-learned while locked)
float US0 = 1080.0, KFF = 1.6;
const float KP = 1.2, KI = 2.5;                     // us per Hz, us per Hz*s
bool armed = false, logging = false;
int throttleUs = 1000;
unsigned long lastCtrl = 0, lastLog = 0, lastBtn = 0;

void hallISR() {
  unsigned long now = micros();
  unsigned long dt = now - lastEdgeUs;
  if (dt > 1500) {               // reject bounce; > 666 Hz is impossible here
    periodUs = dt; lastEdgeUs = now; edgeCount++;
  }
}

float measuredHz() {
  noInterrupts(); unsigned long p = periodUs, last = lastEdgeUs; interrupts();
  if (p == 0 || (micros() - last) > 100000UL) return 0.0;   // no edge for 100 ms -> < 10 Hz
  return 1.0e6 / (float)p;
}

void writeThrottle(int us) {
  throttleUs = constrain(us, 1000, 2000);
  esc.writeMicroseconds(throttleUs);
}

void arm() {
  Serial.println(F("# arming ESC: minimum throttle 3 s"));
  writeThrottle(1000);
  delay(3000);
  armed = true;
  Serial.println(F("# armed"));
}

void status() {
  Serial.print(F("# armed=")); Serial.print(armed);
  Serial.print(F(" target=")); Serial.print(target);
  Serial.print(F(" setpoint=")); Serial.print(setpoint);
  Serial.print(F(" f=")); Serial.print(measuredHz(), 2);
  Serial.print(F(" thr=")); Serial.print(throttleUs);
  Serial.print(F(" land=")); Serial.print(LAND_HZ);
  Serial.print(F(" ff=")); Serial.print(US0); Serial.print('+'); Serial.println(KFF, 3);
}

void handleLine(String s) {
  s.trim(); if (s.length() == 0) return;
  String u = s; u.toUpperCase();
  if (u == "ARM") { arm(); return; }
  if (u == "?") { status(); return; }
  if (u == "L") { target = LAND_HZ; Serial.println(F("# landing")); return; }
  if (u == "X!") { target = 0; setpoint = 0; integ = 0; writeThrottle(1000); Serial.println(F("# STOP")); return; }
  if (u.startsWith("S ")) {
    if (!armed) { Serial.println(F("! not armed (send ARM)")); return; }
    float f = s.substring(2).toFloat();
    if (f < 0 || f > MAX_HZ) { Serial.println(F("! out of range")); return; }
    target = f; Serial.print(F("# target ")); Serial.println(target); return;
  }
  if (u.startsWith("RATE ")) { rampRate = constrain(s.substring(5).toFloat(), 0.5, 100.0); return; }
  if (u.startsWith("LANDHZ ")) { LAND_HZ = constrain(s.substring(7).toFloat(), 50.0, MAX_HZ); return; }
  if (u.startsWith("LOG ")) { logging = s.substring(4).toInt() != 0; return; }
  Serial.println(F("! unknown command"));
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_HALL, INPUT_PULLUP);
  pinMode(PIN_BTN, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  esc.attach(PIN_ESC, 1000, 2000);
  writeThrottle(1000);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL), hallISR, RISING);
  Serial.println(F("# SpinTrap controller ready. Send ARM, then S 200."));
}

String line;
void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') { handleLine(line); line = ""; }
    else if (line.length() < 40) line += c;
  }
  // button (debounced, active low)
  if (digitalRead(PIN_BTN) == LOW && millis() - lastBtn > 400) {
    lastBtn = millis();
    if (!armed) arm();
    else if (target < 1.0) target = DEFAULT_HZ;
    else target = LAND_HZ;
  }

  unsigned long now = millis();
  if (now - lastCtrl >= 20) {                      // 50 Hz control loop
    float dt = (now - lastCtrl) / 1000.0; lastCtrl = now;
    float tgt = target;
    if (USE_POT && tgt > 1.0) tgt += (analogRead(PIN_POT) - 512) * (20.0 / 512.0);
    tgt = constrain(tgt, 0.0, MAX_HZ);
    // slew-limited set point
    float step = rampRate * dt;
    if (setpoint < tgt) setpoint = min(setpoint + step, tgt); else setpoint = max(setpoint - step, tgt);

    float f = measuredHz();
    if (!armed || setpoint < 1.0) {
      writeThrottle(1000); integ = 0;
    } else {
      float e = setpoint - f;
      // integrate only when the tach is alive (avoid wind-up during start)
      if (f > 5.0) integ = constrain(integ + e * dt, -150.0, 150.0);
      float u = US0 + KFF * setpoint + KP * e + KI * integ;
      writeThrottle((int)u);
      // slowly learn the feed-forward offset while locked so integ stays near zero
      if (fabs(e) < 0.5 && f > 50) { US0 += 0.02 * KI * integ * dt; integ *= (1.0 - 0.02 * dt); }
    }
    // tach-loss watchdog
    static unsigned long badSince = 0;
    if (armed && throttleUs > 1150 && f < 1.0) {
      if (badSince == 0) badSince = now;
      if (now - badSince > 300) { target = 0; setpoint = 0; integ = 0; writeThrottle(1000);
        Serial.println(F("! tach lost - throttle cut")); badSince = 0; }
    } else badSince = 0;

    digitalWrite(PIN_LED, (setpoint > 1.0 && fabs(setpoint - f) < 0.5) ? HIGH : LOW);
  }
  if (logging && now - lastLog >= 50) {
    lastLog = now;
    Serial.print(now); Serial.print(','); Serial.print(setpoint, 2); Serial.print(',');
    Serial.print(measuredHz(), 2); Serial.print(','); Serial.println(throttleUs);
  }
}
