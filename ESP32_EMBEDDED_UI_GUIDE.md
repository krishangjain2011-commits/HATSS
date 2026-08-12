# ESP32 Embedded UI in HATSS App

## Overview

The HATSS app now displays the ESP32's web control panel **directly embedded** in the Sensors page as an iframe. This gives you live access to the ESP32 control panel without needing to open a separate browser tab.

## What You Get

When ESP32 is connected, the Sensors page shows:

1. **Sensor Status Cards** (grid of 4)
   - 🔥 Fire detection
   - 👁️ Motion detection  
   - 🛢️ Gas detection
   - 💧 Water level

2. **ESP32 Control Panel** (full interactive UI)
   - All sensor readings from ESP32
   - Real-time status updates
   - Water level gauge with visualization
   - Buzzer control buttons
   - Alarm test functionality
   - System uptime tracking

3. **Backend Fallback**
   - If ESP32 disconnects, data comes from backend
   - Source indicator shows "ESP32" or "Backend"

## How It Works

```
┌─────────────────────────────────────┐
│     HATSS Frontend (React)          │
│  ┌─────────────────────────────────┐│
│  │  Sensors Page                   ││
│  │  ┌──────────────────────────────┐│
│  │  │ Source: ESP32 ⚙️ Setup      ││
│  │  ├──────────────────────────────┤│
│  │  │ Sensor Cards (4 grid)        ││
│  │  ├──────────────────────────────┤│
│  │  │ ESP32 Control Panel          ││
│  │  │ ┌────────────────────────────┤│
│  │  │ │ HATSS Security System  🛡️ ││
│  │  │ │ • IR Motion Sensor        ││
│  │  │ │ • Flame/Fire Sensor       ││
│  │  │ │ • MQ2 Gas Sensor          ││
│  │  │ │ • Water Level             ││
│  │  │ │ • Buzzer Controls         ││
│  │  │ │ • Test Alarm Button       ││
│  │  │ └────────────────────────────┤│
│  │  └──────────────────────────────┘│
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
         ↓ (fetches from)
     192.168.4.1 (ESP32 AP)
         ↓ (alternative)
     Backend API (fallback)
```

## Setup Steps

### 1. Upload ESP32 Code
- Open Arduino IDE
- Load `esp32_integration_code.ino`
- Select ESP32 board
- Upload to device

### 2. Power On ESP32
- Device will broadcast `HATSS_SECURITY_NET` WiFi
- Open Serial Monitor to see IP address (usually `192.168.4.1`)

### 3. Connect to WiFi
On your computer/phone:
- WiFi Settings → `HATSS_SECURITY_NET`
- Password: `HATSS1234`

### 4. Open App
- Go to `http://localhost:5173`
- Navigate to **Sensors** page
- ESP32 UI automatically appears

## Features of Embedded UI

### Real-Time Sensor Display
- **IR Motion**: Shows CLEAR or INTRUSION with color coding
- **Flame/Fire**: Shows SAFE or FIRE! with alerts
- **Gas Sensor**: Shows NORMAL AIR or GAS! with rating 1-10
- **Water Level**: Animated bar with percentage and raw analog value

### Visual Indicators
- Green indicators = Safe/Normal
- Red indicators = Alert/Hazard
- Pulsing red = Active alarm
- Color-coded water bar (blue → yellow → red)

### Control Buttons
- **🔇 Mute Buzzer Alarm**: Silence the buzzer
- **🔔 Test Alarm ON**: Test the alarm system
- Both buttons send commands to ESP32 immediately

### System Information
- **Uptime**: Shows how long ESP32 has been running
- **Connection Status**: 🟢 SYSTEM ACTIVE
- **Backend Link**: Shows connection to HATSS backend

## Manual IP Configuration

If ESP32 doesn't auto-detect:

1. Click **⚙️ Setup** button in Sensors header
2. Enter ESP32 IP manually (e.g., `192.168.1.100`)
3. Click **Save**
4. IP is saved to browser storage for future sessions

## Troubleshooting

### ESP32 UI Not Appearing
- Check you're connected to `HATSS_SECURITY_NET` WiFi
- Verify ESP32 is powered on
- Check Serial Monitor for IP address
- Try manual IP setup with correct IP

### Buttons Not Working (Mute/Test)
- Ensure you're connected to same WiFi as ESP32
- Check firewall isn't blocking port 80
- Verify ESP32 has power and OLED display showing activity

### Embedded UI Shows Errors
- Connection timeout: Check WiFi connection
- CORS errors: Ensure CORS headers are enabled on ESP32
- Refresh the page: Press Ctrl+Shift+R (hard refresh)

### Sensor Readings Not Updating
- Check sensor connections on ESP32
- Verify sensor pins match configuration
- Check Serial Monitor for sensor errors
- Restart ESP32 and try again

## API Endpoints (For Reference)

### Sensor Data (JSON)
```
GET http://192.168.4.1/api/sensors
```
Returns:
```json
{
  "ir": false,           // Motion detected
  "flame": false,        // Fire detected
  "gas": false,          // Gas detected
  "water": 45.5,         // Water level %
  "mq2_rating": 3,       // Gas level 1-10
  "buzzer": false,       // Buzzer active
  "muted": false,        // Buzzer muted
  "raw_water": 2500      // Raw analog value
}
```

### Web UI
```
GET http://192.168.4.1/
```
Returns complete HTML with embedded UI

### Buzzer Control
```
POST http://192.168.4.1/api/buzzer/toggle_mute
POST http://192.168.4.1/api/buzzer/test
```

## Performance Notes

- Updates every 1 second
- Iframe height: 700px (adjustable)
- Uses CORS for cross-origin access
- Timeout: 1.5 seconds per IP attempt
- Tries 4 different IP addresses for auto-detection

## Security Notes

- AP runs on local network only (192.168.4.1)
- No authentication required (local development)
- CORS enabled for same-network access
- Sandbox attribute on iframe restricts capabilities

## What's New vs Previous Version

| Feature | Before | After |
|---------|--------|-------|
| Sensor data | JSON only | Visual UI + JSON |
| Controls | API calls only | Interactive buttons in UI |
| Display | Simple cards | Full ESP32 control panel |
| Updates | Manual refresh needed | Auto-refresh every 1 second |
| Watermark | N/A | Real-time system uptime |
| Colors | Basic theme | Rich visual indicators |
| Responsiveness | Static | Fully interactive |

## Browser Compatibility

✅ Chrome/Chromium 90+
✅ Firefox 88+  
✅ Safari 14+
✅ Edge 90+
⚠️ Mobile browsers: UI optimized for desktop (700px height)

## Next Steps

1. Upload `esp32_integration_code.ino` to your ESP32
2. Power on and verify WiFi broadcast
3. Connect to `HATSS_SECURITY_NET`
4. Open app and view embedded ESP32 UI
5. Test sensor readings and alarm buttons
6. Monitor uptime and system status in real-time
