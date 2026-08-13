#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <HTTPClient.h>

// ====================================================================
// HATSS Security System - ESP32 Integration with Backend API
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
#define ENABLE_BACKEND_SYNC  true  // NEW: Send data to HATSS Backend

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

// WiFi Configuration
const char* WIFI_SSID = "YourWiFiSSID";        // Change to your WiFi network
const char* WIFI_PASS = "YourWiFiPassword";   // Change to your WiFi password
const char* BACKEND_URL = "http://192.168.x.x:8000";  // Change to your backend IP

// WiFi AP Credentials
const char* AP_SSID = "HATSS_SECURITY_NET";    // Access Point name (for direct connection)
const char* AP_PASS = "HATSS1234";             // Access Point password
WebServer server(80);

// Enable both Station and AP modes
#define ENABLE_AP_MODE true  // Enable ESP32 as WiFi hotspot

// Global States
bool buzzerMuted = false;
bool isBuzzerActive = false;
unsigned long lastOledUpdate = 0;
unsigned long lastDebugPrint = 0;
unsigned long lastBackendSync = 0;

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

// ====================================================================
// NEW: Send Sensor Data to HATSS Backend API
// ====================================================================
void syncSensorDataToBackend() {
  if (!ENABLE_BACKEND_SYNC || !ENABLE_WIFI) return;
  
  unsigned long now = millis();
  if (now - lastBackendSync < 5000) return;  // Sync every 5 seconds
  lastBackendSync = now;
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[BACKEND] WiFi not connected, skipping sync");
    return;
  }
  
  HTTPClient http;
  String url = String(BACKEND_URL) + "/api/v1/sensors/data";
  
  // Create JSON payload
  String payload = "{";
  payload += "\"fire\":" + String(flameAlarm ? "true" : "false") + ",";
  payload += "\"pir\":" + String(irAlarm ? "true" : "false") + ",";
  payload += "\"gas\":" + String(gasAlarm ? "true" : "false") + ",";
  payload += "\"water_level\":" + String(waterPercentage);
  payload += "}";
  
  Serial.print("[BACKEND] Sending: ");
  Serial.println(payload);
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(payload);
  
  if (httpResponseCode > 0) {
    Serial.print("[BACKEND] Response Code: ");
    Serial.println(httpResponseCode);
    
    if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.println("[BACKEND] Success!");
    }
  } else {
    Serial.print("[BACKEND] Error: ");
    Serial.println(http.errorToString(httpResponseCode));
  }
  
  http.end();
}

// Alternating Dual-Tone Alarm Siren
void updateBuzzerHardware() {
  if (threatDetected && !buzzerMuted) {
    unsigned long now = millis();
    if (now - lastSirenUpdate >= 150) {
      lastSirenUpdate = now;
      sirenToneToggle = !sirenToneToggle;
      
      int freq = sirenToneToggle ? 2500 : 1800;
      ledcWriteTone(BUZZER_PWM_CHANNEL, freq);
      ledcWrite(BUZZER_PWM_CHANNEL, 128);
    }
  } else {
    ledcWrite(BUZZER_PWM_CHANNEL, 0);
  }
}

// Read Hardware Sensors
void readSensors() {
  rawIR = digitalRead(PIN_IR);
  rawFlame = digitalRead(PIN_FLAME);
  rawMQ2Analog = analogRead(PIN_MQ2);
  
  if (ENABLE_WATER_SENSOR) {
    rawWaterAnalog = analogRead(PIN_WATER);
    waterPercentage = map(rawWaterAnalog, 3500, 1200, 0, 100);
    waterPercentage = constrain(waterPercentage, 0, 100);
  } else {
    rawWaterAnalog = 0;
    waterPercentage = 0;
  }
  
  gasRating = map(rawMQ2Analog, 400, 3600, 1, 10);
  if (gasRating < 1) gasRating = 1;
  if (gasRating > 10) gasRating = 10;
  
  // IR Motion Sensor
  if (ENABLE_IR_SENSOR && rawIR == IR_TRIGGERED) {
    irDebounce++;
    if (irDebounce >= 5) irAlarm = true;
  } else {
    irDebounce = 0;
    irAlarm = false;
  }
  
  // Flame Sensor
  if (ENABLE_FLAME_SENSOR && rawFlame == FLAME_TRIGGERED) {
    flameDebounce++;
    if (flameDebounce >= 5) flameAlarm = true;
  } else {
    flameDebounce = 0;
    flameAlarm = false;
  }
  
  // MQ2 Gas Sensor
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

// Print Diagnostics
void printSerialDiagnostics() {
  unsigned long now = millis();
  if (now - lastDebugPrint >= 1000) {
    lastDebugPrint = now;
    Serial.print("[DIAGNOSTICS] IR(D27)="); Serial.print(rawIR);
    Serial.print(irAlarm ? " [ALERT]" : " [OK]");
    Serial.print(" | FLAME(D32)="); Serial.print(rawFlame);
    Serial.print(flameAlarm ? " [ALERT]" : " [OK]");
    Serial.print(" | MQ2 AO(D33)="); Serial.print(rawMQ2Analog);
    Serial.print(gasAlarm ? " [ALERT]" : " [OK]");
    Serial.print(" | Water(D34)="); Serial.print(waterPercentage); Serial.print("%");
    Serial.print(" | Threat="); Serial.println(threatDetected ? "YES [BUZZER ON]" : "NO [BUZZER OFF]");
  }
}

// Update OLED Display
void updateOLEDDisplay() {
  if (!oledAvailable) return;
  
  unsigned long now = millis();
  if (now - lastOledUpdate < 150) return;
  lastOledUpdate = now;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  // Draw Water Beaker Animation
  display.drawRect(98, 16, 25, 46, SSD1306_WHITE);
  display.drawRect(102, 12, 17, 4, SSD1306_WHITE);
  int fillHeight = map(waterPercentage, 0, 100, 0, 42);
  display.fillRect(100, 60 - fillHeight, 21, fillHeight, SSD1306_WHITE);
  
  if (threatDetected) {
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
    display.setCursor(6, 2);
    display.println("HATSS SECURE");
    display.drawFastHLine(0, 12, 94, SSD1306_WHITE);
    display.setCursor(0, 20);
    display.print("Gas: ");
    display.print(gasRating);
    display.print("/10");
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
  
  display.display();
}

// Web API Handlers
const char INDEX_HTML[] PROGMEM = R"rawliteral(<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>HATSS ESP32 Control</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0a0e16;color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:20px}h1{font-size:24px;margin-bottom:5px;display:flex;align-items:center;gap:10px}h1::before{content:"🛡️"}.subtitle{color:#9ca3af;font-size:12px;margin-bottom:20px}.status-banner{background:linear-gradient(135deg,rgba(16,185,129,0.1),rgba(34,197,94,0.1));border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:15px;margin-bottom:20px}.status-text{color:#10b981;font-weight:600}.uptime{float:right;color:#9ca3af;font-size:12px}.sensor-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:20px}@media(max-width:768px){.sensor-grid{grid-template-columns:repeat(2,1fr)}}.sensor-card{background:rgba(31,41,55,0.6);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:15px;position:relative;overflow:hidden}.sensor-card::before{content:"";position:absolute;top:0;right:0;width:2px;height:100%;background:linear-gradient(180deg,rgba(34,197,94,0.5),transparent)}.sensor-card.alert::before{background:linear-gradient(180deg,rgba(239,68,68,0.8),transparent)}.sensor-label{font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:5px}.sensor-title{font-size:14px;font-weight:600;margin-bottom:8px}.sensor-value{font-size:12px;color:#10b981}.sensor-card.alert .sensor-value{color:#ef4444}.indicator{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;background:#10b981}.sensor-card.alert .indicator{background:#ef4444;box-shadow:0 0 10px rgba(239,68,68,0.5)}.water-section{background:rgba(31,41,55,0.6);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:15px;margin-bottom:20px}.water-label{font-size:11px;color:#9ca3af;text-transform:uppercase;margin-bottom:8px}.water-value{font-size:18px;font-weight:600;color:#3b82f6;margin-bottom:10px}.water-bar{height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden;margin-bottom:8px}.water-fill{height:100%;background:linear-gradient(90deg,#3b82f6,#06b6d4);border-radius:3px;transition:width 0.3s}.water-thresholds{display:flex;justify-content:space-between;font-size:10px;color:#9ca3af}.button-group{display:grid;grid-template-columns:1fr 1fr;gap:10px}.btn{padding:12px 20px;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:13px;transition:all 0.3s}.btn-mute{background:#4b5563;color:#fff}.btn-mute:hover{background:#5a6472}.btn-test{background:#ef4444;color:#fff}.btn-test:hover{background:#dc2626}.btn:active{transform:scale(0.98)}.footer{font-size:11px;color:#9ca3af;margin-top:20px;text-align:center}</style></head><body><h1>HATSS Security System</h1><p class="subtitle">ESP32 Hotspot Server • 0.96" OLED Display</p><div class="status-banner"><span class="status-text">🟢 SYSTEM ACTIVE</span><span class="uptime" id="uptime">Uptime: 0s</span></div><div class="sensor-grid"><div class="sensor-card" id="ir-card"><div class="sensor-label">IR Motion Sensor</div><div class="sensor-title"><span class="indicator" id="ir-indicator"></span>Intrusion Detection</div><div class="sensor-value" id="ir-value">CLEAR</div></div><div class="sensor-card" id="flame-card"><div class="sensor-label">Flame / Fire Sensor</div><div class="sensor-title"><span class="indicator" id="flame-indicator"></span>Fire Detection</div><div class="sensor-value" id="flame-value">SAFE</div></div><div class="sensor-card" id="gas-card"><div class="sensor-label">MQ2 Gas Sensor</div><div class="sensor-title"><span class="indicator" id="gas-indicator"></span>Hazard Gas Detection</div><div class="sensor-value" id="gas-value">NORMAL AIR (1/10)</div></div></div><div class="water-section"><div class="water-label">Water Level Indicator</div><div class="water-value"><span id="water-percentage">0%</span> (<span id="water-raw">0</span>)</div><div class="water-bar"><div class="water-fill" id="water-fill" style="width:0%"></div></div><div class="water-thresholds"><span>0%</span><span>50%</span><span>100%</span></div></div><div style="background:rgba(31,41,55,0.6);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:15px;margin-bottom:20px"><div class="sensor-label">0.96" OLED & Alarm</div><div class="sensor-title" style="margin:8px 0">Buzzer Alarm</div><div class="sensor-value" id="buzzer-status">SILENT</div></div><div class="button-group"><button class="btn btn-mute" onclick="toggleMute()">🔇 Mute Buzzer Alarm</button><button class="btn btn-test" onclick="testAlarm()">🔔 Test Alarm ON</button></div><p class="footer">Connected to HATSS Backend • Real-time Sensor Monitoring</p><script>let startTime=Date.now();function updateStatus(){try{fetch('/api/sensors').then(r=>r.json()).then(data=>{document.getElementById('ir-value').innerText=data.ir?'INTRUSION':'CLEAR';document.getElementById('ir-indicator').style.background=data.ir?'#ef4444':'#10b981';document.getElementById('ir-indicator').style.boxShadow=data.ir?'0 0 10px rgba(239,68,68,0.5)':'none';document.getElementById('ir-card').classList.toggle('alert',data.ir);document.getElementById('flame-value').innerText=data.flame?'FIRE!':'SAFE';document.getElementById('flame-indicator').style.background=data.flame?'#ef4444':'#10b981';document.getElementById('flame-indicator').style.boxShadow=data.flame?'0 0 10px rgba(239,68,68,0.5)':'none';document.getElementById('flame-card').classList.toggle('alert',data.flame);document.getElementById('gas-value').innerText=data.gas?'GAS! ('+data.mq2_rating+'/10)':'NORMAL AIR ('+data.mq2_rating+'/10)';document.getElementById('gas-indicator').style.background=data.gas?'#ef4444':'#10b981';document.getElementById('gas-indicator').style.boxShadow=data.gas?'0 0 10px rgba(239,68,68,0.5)':'none';document.getElementById('gas-card').classList.toggle('alert',data.gas);document.getElementById('water-percentage').innerText=data.water.toFixed(0);document.getElementById('water-raw').innerText=data.raw_water;document.getElementById('water-fill').style.width=Math.min(data.water,100)+'%';let waterColor='#3b82f6';if(data.water>75){waterColor='#ef4444'}else if(data.water>50){waterColor='#f59e0b'}document.getElementById('water-fill').style.background='linear-gradient(90deg,'+waterColor+','+waterColor+')';document.getElementById('buzzer-status').innerText=data.muted?'MUTED':data.buzzer?'ALARM':'SILENT';})}catch(e){console.error(e)}}function updateUptime(){let elapsed=Math.floor((Date.now()-startTime)/1000);let hours=Math.floor(elapsed/3600);let minutes=Math.floor((elapsed%3600)/60);let seconds=elapsed%60;document.getElementById('uptime').innerText='Uptime: '+hours+'h '+minutes+'m '+seconds+'s'}setInterval(updateStatus,1000);setInterval(updateUptime,1000);updateStatus();updateUptime();async function toggleMute(){await fetch('/api/buzzer/toggle_mute',{method:'POST'})}async function testAlarm(){await fetch('/api/buzzer/test',{method:'POST'})}</script></body></html>)rawliteral";

void handleRoot() {
  server.send(200, "text/html", INDEX_HTML);
}

void handleSensorsApi() {
  // Enable CORS headers for ALL responses
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.sendHeader("Content-Type", "application/json");
  
  String json = "{";
  json += "\"ir\":" + String(irAlarm ? "true" : "false") + ",";
  json += "\"flame\":" + String(flameAlarm ? "true" : "false") + ",";
  json += "\"gas\":" + String(gasAlarm ? "true" : "false") + ",";
  json += "\"mq2_rating\":" + String(gasRating) + ",";
  json += "\"buzzer\":" + String(isBuzzerActive ? "true" : "false") + ",";
  json += "\"muted\":" + String(buzzerMuted ? "true" : "false") + ",";
  json += "\"water\":" + String(waterPercentage) + ",";
  json += "\"raw_water\":" + String(rawWaterAnalog);
  json += "}";
  server.send(200, "application/json", json);
}

void handleOptions() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(204);
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
  
  for (int i = 0; i < 6; i++) {
    ledcWriteTone(BUZZER_PWM_CHANNEL, 2500);
    ledcWrite(BUZZER_PWM_CHANNEL, 128);
    delay(150);
    ledcWriteTone(BUZZER_PWM_CHANNEL, 1800);
    ledcWrite(BUZZER_PWM_CHANNEL, 128);
    delay(150);
  }
  ledcWrite(BUZZER_PWM_CHANNEL, 0);
  
  buzzerMuted = oldMute;
  updateBuzzerHardware();
  server.send(200, "application/json", "{\"status\":\"ok\"}");
}

void verifyOLEDConnection() {
  static unsigned long lastCheck = 0;
  unsigned long now = millis();
  if (now - lastCheck < 3000) return;
  lastCheck = now;
  
  Wire.beginTransmission(0x3C);
  byte err1 = Wire.endTransmission();
  Wire.beginTransmission(0x3D);
  byte err2 = Wire.endTransmission();
  bool currentlyConnected = (err1 == 0 || err2 == 0);
  
  if (currentlyConnected) {
    if (!oledAvailable) {
      Serial.println("[OLED] Display detected! Initializing...");
      Wire.begin(PIN_SDA, PIN_SCL);
      Wire.setClock(100000);
      Wire.setTimeOut(50);
      
      if (display.begin(SSD1306_SWITCHCAPVCC, err1 == 0 ? 0x3C : 0x3D)) {
        oledAvailable = true;
        Serial.println("[SUCCESS] OLED connection established!");
      }
    }
  } else {
    if (oledAvailable) {
      Serial.println("[WARNING] OLED disconnected!");
      oledAvailable = false;
    }
  }
}

void setup() {
  setCpuFrequencyMhz(80);
  btStop();
  
  Serial.begin(115200);
  delay(300);
  
  Serial.println("\n====================================================");
  Serial.println(" HATSS ESP32 with Backend Integration");
  Serial.println("====================================================");
  
  // Configure Pins
  pinMode(PIN_IR, INPUT_PULLUP);
  pinMode(PIN_FLAME, INPUT_PULLUP);
  pinMode(PIN_MQ2, INPUT_PULLUP);
  pinMode(PIN_WATER, INPUT);
  
  // Setup LEDC PWM
  ledcSetup(BUZZER_PWM_CHANNEL, 2000, 8);
  ledcAttachPin(PIN_BUZZER, BUZZER_PWM_CHANNEL);
  ledcWrite(BUZZER_PWM_CHANNEL, 0);
  
  // Initialize OLED
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);
  Wire.setTimeOut(50);
  
  if (display.begin(SSD1306_SWITCHCAPVCC, 0x3C) || display.begin(SSD1306_SWITCHCAPVCC, 0x3D)) {
    oledAvailable = true;
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(6, 20);
    display.println("HATSS SECURITY SYSTEM");
    display.setCursor(20, 36);
    display.println("BACKEND INTEGRATED");
    display.display();
    Serial.println("[SUCCESS] 0.96\" SSD1306 OLED ready!");
  }
  
  if (ENABLE_WIFI) {
    WiFi.mode(WIFI_AP_STA);  // Both AP and Station mode
    
    // Station Mode - Connect to your home WiFi
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    
    Serial.print("Connecting to WiFi: ");
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n[WiFi Station] Connected!");
      Serial.print("IP Address: ");
      Serial.println(WiFi.localIP());
    } else {
      Serial.println("\n[WiFi Station] Connection failed!");
    }
    
    // Access Point Mode - Create direct connection point
    if (ENABLE_AP_MODE) {
      WiFi.softAP(AP_SSID, AP_PASS);
      IPAddress apIP = WiFi.softAPIP();
      Serial.println("[WiFi AP] Access Point started!");
      Serial.print("[WiFi AP] AP Name: ");
      Serial.println(AP_SSID);
      Serial.print("[WiFi AP] AP IP: ");
      Serial.println(apIP);
      Serial.println("[WiFi AP] Connect from your device to fetch sensor data!");
    }
    
    // Setup Web Server
    server.on("/", handleRoot);
    server.on("/api/sensors", HTTP_GET, handleSensorsApi);
    server.on("/api/sensors", HTTP_OPTIONS, handleOptions);
    server.on("/api/buzzer/toggle_mute", HTTP_POST, handleToggleMute);
    server.on("/api/buzzer/test", HTTP_POST, handleTestAlarm);
    server.begin();
    Serial.println("[Web Server] Started!");
  } else {
    WiFi.mode(WIFI_OFF);
    Serial.println("[POWER SAVE] WiFi disabled. Running offline mode.");
  }
  
  Serial.println("Setup Complete!");
}

void loop() {
  verifyOLEDConnection();
  
  if (ENABLE_WIFI) {
    server.handleClient();
    
    // NEW: Sync sensor data to backend
    if (ENABLE_BACKEND_SYNC) {
      syncSensorDataToBackend();
    }
  }
  
  readSensors();
  printSerialDiagnostics();
  updateBuzzerHardware();
  updateOLEDDisplay();
  
  delay(10);
}
