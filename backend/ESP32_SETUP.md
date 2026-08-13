# HATSS ESP32 Sensor Integration Setup

## Overview

The ESP32 integration code (`esp32_integration_code.ino`) provides two ways to access real-time sensor data:

### 1. Access Point (AP) Mode (Recommended for Frontend)
The ESP32 creates its own WiFi hotspot that the frontend can connect to directly.

**Configuration in ESP32 code:**
```cpp
const char* AP_SSID = "HATSS_SECURITY_NET";    // WiFi network name
const char* AP_PASS = "HATSS1234";             // WiFi password
```

**Steps to use:**
1. Upload `esp32_integration_code.ino` to ESP32
2. Open Serial Monitor to see the ESP32's IP (default: `192.168.4.1`)
3. From your computer/phone, connect to WiFi network: `HATSS_SECURITY_NET` (password: `HATSS1234`)
4. Open app at `http://localhost:5173`
5. Navigate to Sensors section - should auto-detect ESP32
6. Click ⚙️ Setup button if manual IP entry needed
7. Sensor data should now show "ESP32" as the source

### 2. Station Mode (For Backend Synchronization)
The ESP32 connects to your home WiFi and sends data to the backend.

**Configuration in ESP32 code:**
```cpp
const char* WIFI_SSID = "YourWiFiSSID";       // Your WiFi network
const char* WIFI_PASS = "YourWiFiPassword";   // Your WiFi password
const char* BACKEND_URL = "http://192.168.x.x:8000";  // Backend server IP
```

**Steps to use:**
1. Edit the WiFi credentials in the code
2. Find your backend server IP (run `ipconfig` and look for your computer's IP)
3. Update `BACKEND_URL` with your IP (e.g., `http://192.168.1.100:8000`)
4. Upload to ESP32
5. Data will sync to backend every 5 seconds

## Frontend ESP32 Data Fetching

The frontend (`SensorMonitor.tsx`) now features:
1. **Auto-detection** - Automatically tries multiple ESP32 IP addresses
2. **Smart fallback** - Remembers working IP for faster future connections
3. **Graceful degradation** - Falls back to backend if ESP32 unavailable
4. **Manual control** - Click ⚙️ Setup to manually set ESP32 IP
5. **Live status** - Shows "ESP32" or "Backend" as data source

### Tried IP Addresses (in order):
- Last known working IP (from browser storage)
- `192.168.4.1` (default AP mode)
- `192.168.1.100` (common WiFi router)
- `10.0.0.1` (alternative WiFi)

### API Endpoint
**ESP32 Endpoint:** `GET /api/sensors`

**Response format:**
```json
{
  "ir": false,           // Motion sensor (true = motion detected)
  "flame": false,        // Fire sensor (true = fire detected)
  "gas": false,          // Gas sensor (true = gas detected)
  "water": 45.5,         // Water level percentage (0-100)
  "mq2_rating": 3,       // Gas level rating (1-10)
  "buzzer": false,       // Buzzer active
  "muted": false,        // Buzzer muted
  "raw_water": 2500      // Raw analog reading
}
```

## Using the Setup Button

The Sensors section includes a ⚙️ Setup button that lets you:
- View current ESP32 AP name: `HATSS_SECURITY_NET`
- See currently saved ESP32 IP
- Manually enter a different IP if auto-detection fails
- Save the IP to browser storage for future sessions

## Troubleshooting

### ESP32 not showing up in app
- **Check WiFi**: Ensure you're connected to `HATSS_SECURITY_NET` network
- **Verify ESP32**: ESP32 must be powered on and running the sketch
- **Check Serial Monitor**: Look for startup messages and connection status
- **Manual setup**: Click ⚙️ Setup and enter ESP32 IP manually (check Serial Monitor for IP)
- **Wait for connection**: Initial detection may take up to 5 seconds

### Sensor data not updating
- **For AP mode**: Device must be on same WiFi network as ESP32
- **For Station mode**: Verify backend URL is correct in ESP32 code
- **Sensor pins**: Check all sensor connections are secure
- **Serial output**: Monitor Serial Monitor for error messages
- **Timeouts**: If timing out, try manual IP configuration

### High false positive detections
- **IR Sensor**: Wait 60 seconds after power-on for proper calibration
- **Flame Sensor**: Keep away from bright ambient light
- **Gas Sensor**: Adjust `MQ2_ANALOG_THRESHOLD` constant (default: 2200)

## Hardware Connections

```
ESP32 Pin -> Component
GPIO 27   -> IR Motion Sensor DO
GPIO 32   -> Flame Sensor DO
GPIO 33   -> MQ2 Gas Sensor AO (Analog)
GPIO 34   -> Water Level Sensor (Analog)
GPIO 25   -> Buzzer
GPIO 21   -> OLED SDA
GPIO 22   -> OLED SCL
```

## Features

✅ Real-time sensor data via WiFi  
✅ Dual WiFi mode (AP + Station simultaneously)  
✅ Auto-detection of ESP32 on network  
✅ Smart IP caching and fallback  
✅ Manual IP configuration via UI  
✅ OLED display with real-time alerts  
✅ Buzzer with mute control  
✅ Local web control panel  
✅ Backend synchronization every 5 seconds  
✅ CORS enabled for browser requests

## Quick Start

1. **Upload ESP32 Code**
   - Open Arduino IDE
   - Load `esp32_integration_code.ino`
   - Select ESP32 board and COM port
   - Click Upload
   - Monitor Serial output for startup messages

2. **Connect to WiFi AP**
   - On your device: WiFi Settings → `HATSS_SECURITY_NET`
   - Password: `HATSS1234`
   - Connected status shown by green indicator

3. **Open Application**
   - Go to `http://localhost:5173`
   - Navigate to Sensors section
   - Should show "ESP32" as source with green dot
   - Auto-refreshes every 1 second

4. **Test Sensors**
   - **Motion**: Wave hand in front of IR sensor
   - **Fire**: Light near flame sensor
   - **Gas**: Hold lighter or gas source near MQ2 sensor
   - **Water**: Pour water near water level sensor
   - All should trigger visual alerts in app

## Configuration Reference

**ESP32 Code Locations:**

Station WiFi (line ~52):
```cpp
const char* WIFI_SSID = "YourWiFiSSID";
const char* WIFI_PASS = "YourWiFiPassword";
const char* BACKEND_URL = "http://192.168.x.x:8000";
```

Access Point WiFi (line ~56):
```cpp
const char* AP_SSID = "HATSS_SECURITY_NET";
const char* AP_PASS = "HATSS1234";
```

Gas Sensor Threshold (line ~42):
```cpp
#define MQ2_ANALOG_THRESHOLD 2200  // Adjust for sensitivity
```

Enable/Disable Features (line ~33):
```cpp
#define ENABLE_AP_MODE true  // Create WiFi hotspot
#define ENABLE_BACKEND_SYNC true  // Send to backend
```
