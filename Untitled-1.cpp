include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ====================================================================
// HATSS Security System - SSD1306 OLED, Custom Siren, & Water Level
// ====================================================================
// Hardware Pin Assignments:
// - IR Motion Sensor DO   -> GPIO 27 (D27) [Reversed Logic: Active LOW]
// - Flame Sensor DO        -> GPIO 32 (D32)
// - MQ2 Gas Sensor AO      -> GPIO 33 (D33) [Analog Output AO]
// - Soil Moisture (Water) -> GPIO 34 (D34) [Analog Output A0]
// - Active/Passive Buzzer  -> GPIO 25 (D25) [LEDC Dual-Tone Alarm Siren]
// - 0.96" OLED I2C SDA     -> GPIO 21 (D21)
// - 0.96" OLED I2C SCL     -> GPIO 22 (D22)
// ====================================================================

#define PIN_IR     27
#define PIN_FLAME  32
#define PIN_MQ2    33
#define PIN_WATER  34
#define PIN_BUZZER 25
#define PIN_SDA    21
#define PIN_SCL    22

// Sensor Enable Switches
#define ENABLE_IR_SENSOR     true
#define ENABLE_FLAME_SENSOR  true
#define ENABLE_MQ2_SENSOR    true
#define ENABLE_WATER_SENSOR  true
#define ENABLE_WIFI          true

// Sensor Logic Levels:
#define IR_TRIGGERED    LOW   // Reversed Active LOW logic
#define FLAME_TRIGGERED LOW   // Active LOW logic

// MQ2 Gas Sensor Analog Threshold (For A0 pin connection on GPIO 33)
#define MQ2_ANALOG_THRESHOLD 2200

// 0.96" OLED Display Configuration (128x64, SSD1306)
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
bool oledAvailable = false;

// WiFi AP Credentials
const char* AP_SSID = "HATSS_SECURITY_NET";
const char* AP_PASS = "HATSS1234";

WebServer server(80);

// Global States
bool buzzerMuted = false;
bool isBuzzerActive = false;
unsigned long lastOledUpdate = 0;
unsigned long lastDebugPrint = 0;

// LEDC Siren Tune Configuration
#define BUZZER_PWM_CHANNEL  0
unsigned long lastSirenUpdate = 0;
bool sirenToneToggle = false;

// Sensor States
int rawIR = 1;
int rawFlame = 1;
int rawMQ2Analog = 0;
int rawWaterAnalog = 0;
int gasRating = 1;
int waterPercentage = 0;

bool irAlarm = false;
bool flameAlarm = false;
bool gasAlarm = false;
bool threatDetected = false;

// Debounce Counters
int irDebounce = 0;
int flameDebounce = 0;
int gasDebounce = 0;

// Alternating Dual-Tone Alarm Siren (Alternates 2.5kHz and 1.8kHz every 150ms for maximum loudness!)
void updateBuzzerHardware() {
  if (threatDetected && !buzzerMuted) {
    unsigned long now = millis();
    if (now - lastSirenUpdate >= 150) { // Alternates pitch every 150ms
      lastSirenUpdate = now;
      sirenToneToggle = !sirenToneToggle;
     
      int freq = sirenToneToggle ? 2500 : 1800; // Alternating pitches
      ledcWriteTone(BUZZER_PWM_CHANNEL, freq);
      ledcWrite(BUZZER_PWM_CHANNEL, 128); // Play at 50% duty cycle (Maximum volume)
    }
  } else {
    ledcWrite(BUZZER_PWM_CHANNEL, 0); // Silent when safe
  }
}

// Read Hardware Sensors Safely (Including Water Soil Moisture Sensor)
void readSensors() {
  rawIR = digitalRead(PIN_IR);
  rawFlame = digitalRead(PIN_FLAME);
  rawMQ2Analog = analogRead(PIN_MQ2);
 
  if (ENABLE_WATER_SENSOR) {
    rawWaterAnalog = analogRead(PIN_WATER);
    // Standard soil moisture / analog water sensor has high value when dry (~3500) and low value when fully wet (~1200)
    waterPercentage = map(rawWaterAnalog, 3500, 1200, 0, 100);
    waterPercentage = constrain(waterPercentage, 0, 100);
  } else {
    rawWaterAnalog = 0;
    waterPercentage = 0;
  }

  // Map Analog ADC to 1-10 rating for display purposes
  gasRating = map(rawMQ2Analog, 400, 3600, 1, 10);
  if (gasRating < 1) gasRating = 1;
  if (gasRating > 10) gasRating = 10;

  // 1. IR Motion Sensor
  if (ENABLE_IR_SENSOR && rawIR == IR_TRIGGERED) {
    irDebounce++;
    if (irDebounce >= 5) irAlarm = true;
  } else {
    irDebounce = 0;
    irAlarm = false;
  }

  // 2. Flame Sensor
  if (ENABLE_FLAME_SENSOR && rawFlame == FLAME_TRIGGERED) {
    flameDebounce++;
    if (flameDebounce >= 5) flameAlarm = true;
  } else {
    flameDebounce = 0;
    flameAlarm = false;
  }

  // 3. MQ2 Gas Sensor (AO)
  if (ENABLE_MQ2_SENSOR && rawMQ2Analog > MQ2_ANALOG_THRESHOLD) {
    gasDebounce++;
    if (gasDebounce >= 5) gasAlarm = true;
  } else {
    gasDebounce = 0;
    gasAlarm = false;
  }

  threatDetected = (irAlarm || flameAlarm || gasAlarm);
  isBuzzerActive = threatDetected;
}

// Print Diagnostics to Serial Monitor
void printSerialDiagnostics() {
  unsigned long now = millis();
  if (now - lastDebugPrint >= 1000) {
    lastDebugPrint = now;
    Serial.print("[DIAGNOSTICS] IR(D27)="); Serial.print(rawIR);
    Serial.print(irAlarm ? " [ALERT]" : " [OK]");
    Serial.print(" | FLAME(D32)="); Serial.print(rawFlame);
    Serial.print(flameAlarm ? " [ALERT]" : " [OK]");
    Serial.print(" | MQ2 AO(D33)="); Serial.print(rawMQ2Analog);
    Serial.print(" (Thresh="); Serial.print(MQ2_ANALOG_THRESHOLD); Serial.print(")");
    Serial.print(gasAlarm ? " [ALERT]" : " [OK]");
    Serial.print(" | Water(D34)="); Serial.print(waterPercentage); Serial.print("% ("); Serial.print(rawWaterAnalog); Serial.print(")");
    Serial.print(" | Threat="); Serial.println(threatDetected ? "YES [BUZZER ON]" : "NO [BUZZER OFF]");
  }
}

// Render 0.96" SSD1306 OLED Display (Clean Layout, Spacing, and Live Beaker Animation)
void updateOLEDDisplay() {
  if (!oledAvailable) return;
 
  unsigned long now = millis();
  if (now - lastOledUpdate < 150) return;
  lastOledUpdate = now;

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  // Draw Water Beaker Animation on the Right (Consistent in both modes)
  // Outer Beaker Border
  display.drawRect(98, 16, 25, 46, SSD1306_WHITE);
  // Beaker Cap
  display.drawRect(102, 12, 17, 4, SSD1306_WHITE);
  // Fill beaker with fluid
  int fillHeight = map(waterPercentage, 0, 100, 0, 42);
  display.fillRect(100, 60 - fillHeight, 21, fillHeight, SSD1306_WHITE);

  if (threatDetected) {
    // Alert Mode Display
    display.setCursor(6, 2);
    display.println("! THREAT ALERT !");
    display.drawFastHLine(0, 12, 94, SSD1306_WHITE);

    display.setCursor(0, 20);
    if (flameAlarm) {
      display.println("-> FIRE!");
    } else if (irAlarm) {
      display.println("-> INTRUSION");
    } else if (gasAlarm) {
      display.print("-> GAS: ");
      display.print(gasRating);
      display.println("/10");
    }

    display.setCursor(0, 36);
    display.println("EVACUATE AREA");

    display.setCursor(0, 52);
    display.print("BUZ: ");
    display.println(buzzerMuted ? "MUTED" : "ALARM");

  } else {
    // Normal Secure Mode Display
    display.setCursor(6, 2);
    display.println("HATSS SECURE");
    display.drawFastHLine(0, 12, 94, SSD1306_WHITE);

    display.setCursor(0, 20);
    display.print("Gas: ");
    display.print(gasRating);
    display.print("/10 (");
    display.print(rawMQ2Analog);
    display.println(")");

    display.setCursor(0, 31);
    display.print("Fire: ");
    display.println(flameAlarm ? "ALERT" : "SAFE");

    display.setCursor(0, 42);
    display.print("IR  : ");
    display.println(irAlarm ? "ALERT" : "CLEAR");

    display.setCursor(0, 53);
    display.print("Water: ");
    display.print(waterPercentage);
    display.println("%");
  }

  display.display(); // SSD1306 native frame flush
}

// Embedded Web Dashboard HTML
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HATSS - Security System</title>
  <style>
    :root { --bg-dark: #090d16; --card-bg: rgba(17, 24, 39, 0.85); --card-border: rgba(255, 255, 255, 0.08); --text-main: #f3f4f6; --text-muted: #9ca3af; --accent-blue: #3b82f6; --accent-green: #10b981; --accent-red: #ef4444; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
    body { background-color: var(--bg-dark); color: var(--text-main); padding: 15px; min-height: 100vh; }
    .container { max-width: 900px; margin: 0 auto; }
    header { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .threat-banner { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    .threat-banner.alert-active { border-color: var(--accent-red); background: rgba(239, 68, 68, 0.12); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 20px; }
    .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 20px; }
    .card-title { font-size: 13px; font-weight: 600; color: var(--text-muted); }
    .card-value { font-size: 17px; font-weight: 700; margin-top: 4px; }
    .state-tag { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; margin-top: 10px; }
    .state-safe { background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3); }
    .state-danger { background: rgba(239, 68, 68, 0.2); color: var(--accent-red); border: 1px solid rgba(239, 68, 68, 0.5); }
    .controls-panel { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 20px; margin-bottom: 20px; display: flex; gap: 12px; }
    .btn { flex: 1; padding: 12px 20px; border-radius: 12px; border: none; font-weight: 700; cursor: pointer; }
    .btn-mute { background: #374151; color: #fff; }
    .btn-alarm { background: var(--accent-red); color: #fff; }
   
    /* CSS Fluid Beaker Water Tank Animation */
    .tank-container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
    }
    .tank {
      position: relative;
      width: 46px;
      height: 75px;
      border: 2px solid rgba(255, 255, 255, 0.25);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.03);
      overflow: hidden;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    }
    .water {
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      background: linear-gradient(0deg, #1d4ed8 0%, #3b82f6 100%);
      transition: height 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .water::before {
      content: "";
      position: absolute;
      width: 200%;
      height: 8px;
      background: rgba(255, 255, 255, 0.25);
      top: -4px;
      left: -50%;
      border-radius: 38%;
      animation: wave 3s infinite linear;
    }
    @keyframes wave {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div style="display:flex; align-items:center; gap:12px;">
        <div style="font-size:24px;">🛡️</div>
        <div>
          <h1 style="font-size:20px; font-weight:bold;">HATSS Security System</h1>
          <p style="font-size:11px; color:#9ca3af;">ESP32 Hotspot Server • 0.96" OLED Display</p>
        </div>
      </div>
      <div style="padding:6px 14px; border-radius:20px; font-size:12px; font-weight:600; background:rgba(16,185,129,0.15); color:#10b981;">
        SYSTEM ACTIVE
      </div>
    </header>

    <div class="threat-banner" id="threatBanner">
      <div>
        <div style="font-size:13px; color:#9ca3af; text-transform:uppercase;">Overall System Security</div>
        <div id="overallStatus" style="font-size:22px; font-weight:800; color:#10b981;">SYSTEM SECURE</div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:12px; color:#9ca3af;">Uptime</div>
        <div id="uptimeText" style="font-weight:700; font-family:monospace;">0s</div>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-title">IR MOTION SENSOR</div>
        <div class="card-value">Intrusion Detected</div>
        <span class="state-tag state-safe" id="tagIR">ALL CLEAR</span>
      </div>
      <div class="card">
        <div class="card-title">FLAME / FIRE SENSOR</div>
        <div class="card-value">Fire Detected</div>
        <span class="state-tag state-safe" id="tagFlame">NO FIRE</span>
      </div>
      <div class="card">
        <div class="card-title">MQ2 GAS SENSOR</div>
        <div class="card-value">Hazard Gas Detected</div>
        <span class="state-tag state-safe" id="tagGas">NORMAL AIR (1/10)</span>
      </div>
      <div class="card">
        <div class="card-title">0.96" OLED & ALARM</div>
        <div class="card-value">Buzzer Alarm</div>
        <span class="state-tag state-safe" id="tagBuzzer">SILENT</span>
      </div>
     
      <!-- Water Level Indicator Card with wave fluid animation -->
      <div class="card">
        <div class="tank-container">
          <div>
            <div class="card-title">WATER LEVEL INDICATOR</div>
            <div class="card-value" id="waterVal">0% (0)</div>
            <span class="state-tag state-safe" id="tagWater">NORMAL</span>
          </div>
          <div class="tank">
            <div class="water" id="waterFluid" style="height: 0%;"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="controls-panel">
      <button class="btn btn-mute" onclick="toggleMute()"><span id="muteBtnText">Mute Buzzer Alarm</span></button>
      <button class="btn btn-alarm" onclick="triggerTestAlarm()">🚨 Test Alarm ON</button>
    </div>
  </div>

  <script>
    async function fetchSensorData() {
      try {
        const res = await fetch('/api/sensors');
        const data = await res.json();

        document.getElementById('tagIR').className = data.ir ? 'state-tag state-danger' : 'state-tag state-safe';
        document.getElementById('tagIR').innerText = data.ir ? '🚨 INTRUSION DETECTED!' : 'NORMAL';

        document.getElementById('tagFlame').className = data.flame ? 'state-tag state-danger' : 'state-tag state-safe';
        document.getElementById('tagFlame').innerText = data.flame ? '🔥 FIRE DETECTED!' : 'SAFE';

        document.getElementById('tagGas').className = data.gas ? 'state-tag state-danger' : 'state-tag state-safe';
        document.getElementById('tagGas').innerText = data.gas ? '💨 HAZARD GAS! (' + data.mq2_rating + '/10)' : 'NORMAL AIR (' + data.mq2_rating + '/10)';

        document.getElementById('tagBuzzer').className = data.buzzer ? 'state-tag state-danger' : 'state-tag state-safe';
        document.getElementById('tagBuzzer').innerText = data.buzzer ? (data.muted ? '🔇 SIREN MUTED' : '🚨 SIREN PLAYING!') : 'SILENT';

        // Live Water Level Updates & CSS Wave Animation
        document.getElementById('waterVal').innerText = data.water + '% (' + data.raw_water + ')';
        document.getElementById('waterFluid').style.height = data.water + '%';
       
        const tagWater = document.getElementById('tagWater');
        if (data.water <= 15) {
          tagWater.className = 'state-tag state-danger';
          tagWater.innerText = '🚨 WATER LEVEL LOW!';
        } else {
          tagWater.className = 'state-tag state-safe';
          tagWater.innerText = 'WATER LEVEL SAFE';
        }

        const threatBanner = document.getElementById('threatBanner');
        const overallStatus = document.getElementById('overallStatus');
        if (data.ir || data.flame || data.gas) {
          threatBanner.className = 'threat-banner alert-active';
          overallStatus.innerText = '🚨 THREAT DETECTED!';
          overallStatus.style.color = '#ef4444';
        } else {
          threatBanner.className = 'threat-banner';
          overallStatus.innerText = 'SYSTEM SECURE';
          overallStatus.style.color = '#10b981';
        }
        document.getElementById('uptimeText').innerText = data.uptime + 's';
      } catch (err) {}
    }

    async function toggleMute() {
      const res = await fetch('/api/buzzer/toggle_mute', { method: 'POST' });
      const data = await res.json();
      document.getElementById('muteBtnText').innerText = data.muted ? 'Unmute Buzzer' : 'Mute Buzzer Alarm';
    }

    async function triggerTestAlarm() {
      await fetch('/api/buzzer/test', { method: 'POST' });
    }

    setInterval(fetchSensorData, 1000);
    fetchSensorData();
  </script>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", INDEX_HTML);
}

void handleSensorsApi() {
  String json = "{";
  json += "\"ir\":" + String(irAlarm ? "true" : "false") + ",";
  json += "\"flame\":" + String(flameAlarm ? "true" : "false") + ",";
  json += "\"gas\":" + String(gasAlarm ? "true" : "false") + ",";
  json += "\"mq2_rating\":" + String(gasRating) + ",";
  json += "\"buzzer\":" + String(isBuzzerActive ? "true" : "false") + ",";
  json += "\"muted\":" + String(buzzerMuted ? "true" : "false") + ",";
  json += "\"water\":" + String(waterPercentage) + ",";
  json += "\"raw_water\":" + String(rawWaterAnalog) + ",";
  json += "\"uptime\":" + String(millis() / 1000);
  json += "}";

  server.send(200, "application/json", json);
}

void handleToggleMute() {
  buzzerMuted = !buzzerMuted;
  updateBuzzerHardware();
  String json = "{\"muted\":" + String(buzzerMuted ? "true" : "false") + "}";
  server.send(200, "application/json", json);
}

void handleTestAlarm() {
  bool oldMute = buzzerMuted;
  buzzerMuted = false;
 
  // Play a quick 1.8-second alternating full-volume test alarm tune
  for (int i = 0; i < 6; i++) {
    ledcWriteTone(BUZZER_PWM_CHANNEL, 2500);
    ledcWrite(BUZZER_PWM_CHANNEL, 128);
    delay(150);
    ledcWriteTone(BUZZER_PWM_CHANNEL, 1800);
    ledcWrite(BUZZER_PWM_CHANNEL, 128);
    delay(150);
  }
  ledcWrite(BUZZER_PWM_CHANNEL, 0); // Stop
 
  buzzerMuted = oldMute;
  updateBuzzerHardware();
  server.send(200, "application/json", "{\"status\":\"ok\"}");
}

// Auto-healing connection check: detects loose wiring/resets and automatically restores the OLED
void verifyOLEDConnection() {
  static unsigned long lastCheck = 0;
  unsigned long now = millis();
  if (now - lastCheck < 3000) return; // Check every 3 seconds
  lastCheck = now;

  // Probe both potential I2C addresses
  Wire.beginTransmission(0x3C);
  byte err1 = Wire.endTransmission();
 
  Wire.beginTransmission(0x3D);
  byte err2 = Wire.endTransmission();

  bool currentlyConnected = (err1 == 0 || err2 == 0);

  if (currentlyConnected) {
    // If the OLED is physically connected but our code hasn't initialized it yet:
    if (!oledAvailable) {
      Serial.println("[OLED] Display detected! Initializing...");
     
      // Re-init Wire interface at standard noise-immune speed
      Wire.begin(PIN_SDA, PIN_SCL);
      Wire.setClock(100000); // 100kHz standard speed (prevents crashes from wire noise!)
      Wire.setTimeOut(50);
     
      // Initialize SSD1306 Display
      if (display.begin(SSD1306_SWITCHCAPVCC, err1 == 0 ? 0x3C : 0x3D)) {
        oledAvailable = true;
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);
        display.display();
        Serial.println("[SUCCESS] OLED connection established and initialized!");
      }
    }
  } else {
    // Display is not connected or has locked up:
    if (oledAvailable) {
      Serial.println("[WARNING] OLED disconnected or crashed! Marking as offline...");
      oledAvailable = false; // Set to false so we re-init on next check
     
      // Clear stuck I2C SDA/SCL lines (I2C Bus Recovery)
      pinMode(PIN_SDA, INPUT_PULLUP);
      pinMode(PIN_SCL, OUTPUT);
      for (int i = 0; i < 9; i++) {
        digitalWrite(PIN_SCL, LOW);
        delayMicroseconds(5);
        digitalWrite(PIN_SCL, HIGH);
        delayMicroseconds(5);
      }
      // Set Stop condition
      pinMode(PIN_SDA, OUTPUT);
      digitalWrite(PIN_SDA, LOW);
      delayMicroseconds(5);
      digitalWrite(PIN_SCL, HIGH);
      delayMicroseconds(5);
      digitalWrite(PIN_SDA, HIGH);
      delayMicroseconds(5);
    }
  }
}

void setup() {
  // --- SOFTWARE POWER OPTIMIZATIONS ---
  setCpuFrequencyMhz(80); // Reduce CPU clock speed from 240MHz to 80MHz (Saves up to 40% current)
  btStop();               // Disable Bluetooth module completely
 
  Serial.begin(115200);
  delay(300);
  Serial.println("\n====================================================");
  Serial.println(" 🛡️ HATSS ESP32 SSD1306 0.96\" OLED & Water Sensor");
  Serial.println("====================================================");

  // Configure Pins
  pinMode(PIN_IR, INPUT_PULLUP);
  pinMode(PIN_FLAME, INPUT_PULLUP);
  pinMode(PIN_MQ2, INPUT_PULLUP);
  pinMode(PIN_WATER, INPUT); // Analog Soil Moisture Input
 
  // Setup LEDC PWM channel for alternating dual-tone alarm melody
  ledcSetup(BUZZER_PWM_CHANNEL, 2000, 8); // Setup
  ledcAttachPin(PIN_BUZZER, BUZZER_PWM_CHANNEL);
  ledcWrite(BUZZER_PWM_CHANNEL, 0); // Start silent

  // Initialize SSD1306 Library (0x3C with 0x3D fallback)
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000); // 100kHz standard speed (noise immune)
  Wire.setTimeOut(50); // Avoid infinite I2C waiting loops

  if (display.begin(SSD1306_SWITCHCAPVCC, 0x3C) || display.begin(SSD1306_SWITCHCAPVCC, 0x3D)) {
    oledAvailable = true;
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
   
    // Splash screen message
    display.setCursor(6, 20);
    display.println("HATSS SECURITY SYSTEM");
    display.setCursor(30, 36);
    display.println("OLED & WATER");
    display.display();
    Serial.println("[SUCCESS] 0.96\" SSD1306 OLED ready!");
  } else {
    Serial.println("[ERROR] OLED Display failed to allocate.");
  }

  if (ENABLE_WIFI) {
    // WiFi AP Setup with Power Spikes Reduction
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    WiFi.setTxPower(WIFI_POWER_11dBm); // Reduce transmit power to save up to 100mA peak current

    IPAddress apIP = WiFi.softAPIP();
    Serial.print("ESP32 Hotspot SSID: ");
    Serial.println(AP_SSID);
    Serial.print("ESP32 Hotspot IP   : ");
    Serial.println(apIP);

    server.on("/", handleRoot);
    server.on("/api/sensors", HTTP_GET, handleSensorsApi);
    server.on("/api/buzzer/toggle_mute", HTTP_POST, handleToggleMute);
    server.on("/api/buzzer/test", HTTP_POST, handleTestAlarm);

    server.begin();
    Serial.println("HATSS Web Server Started Successfully!");
  } else {
    // Disable WiFi radio completely to save ~250mA current!
    WiFi.mode(WIFI_OFF);
    Serial.println("[POWER SAVE] WiFi disabled. Running offline mode.");
  }
}

void loop() {
  // Auto-healing connection check (automatically restores OLED if it disconnects/crashes)
  verifyOLEDConnection();

  if (ENABLE_WIFI) {
    server.handleClient();
  }

  // 1. Read Hardware Sensors
  readSensors();

  // 2. Output Diagnostics to Serial Monitor
  printSerialDiagnostics();

  // 3. Simple ON/OFF Buzzer Control
  updateBuzzerHardware();

  // 4. Update OLED Display
  updateOLEDDisplay();
}