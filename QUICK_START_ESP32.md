# Quick Start: Connect to ESP32 and View Live Sensor Data

## Step 1: Upload ESP32 Code
1. Open **Arduino IDE**
2. Open file: `backend/esp32_integration_code.ino`
3. Select board: **ESP32 Dev Module**
4. Select COM port where ESP32 is connected
5. Click **Upload**
6. Watch Serial Monitor for startup messages

## Step 2: Power On ESP32
- Once uploaded, ESP32 will automatically start
- It will broadcast a WiFi hotspot: `HATSS_SECURITY_NET`
- Check Serial Monitor to see IP address (usually `192.168.4.1`)

## Step 3: Connect Your Computer to ESP32 Hotspot
**On Windows:**
1. Click WiFi icon in system tray
2. Select `HATSS_SECURITY_NET`
3. Password: `HATSS1234`
4. Click Connect

**On Mac:**
1. Click WiFi icon in menu bar
2. Select `HATSS_SECURITY_NET`
3. Password: `HATSS1234`

**On Android/iPhone:**
1. WiFi Settings → `HATSS_SECURITY_NET`
2. Password: `HATSS1234`

## Step 4: Open HATSS App
- Go to: `http://localhost:5173`
- Navigate to **Sensors** page
- You should see:
  - 🟢 Connected indicator (green, pulsing)
  - IP shown as: `192.168.4.1`

## Step 5: View Live Data

### Live Water Level Indicator
- Shows current water level as percentage
- Color-coded (blue → yellow → red)
- Status badge: LOW, MEDIUM, HIGH, or CRITICAL
- Smooth animated bar
- Threshold markers (0%, 25%, 50%, 75%, 100%)
- Alert warning when >75% capacity

### Live Air Quality Indicator
- Shows MQ2 gas sensor rating (0-10)
- Color-coded by quality:
  - 🟢 0-2: EXCELLENT (green)
  - 🔵 2-4: GOOD (blue)
  - 🟡 4-6: MODERATE (yellow)
  - 🟠 6-8: POOR (orange)
  - 🔴 8-10: HAZARDOUS (red)
- Visual scale bar
- Animated gauge updates every 1 second
- Color legend for reference
- Alert when gas detected

### Sensor Alert Cards
4 quick status cards:
- 🔥 Fire detection (on/off)
- 👁️ Motion detection (on/off)
- 🛢️ Gas detection (on/off)
- 💧 Water alert (on/off when >75%)

## What Happens Behind the Scenes

1. **App loads** → Sensors page opens
2. **Every 1 second** → App fetches from `http://192.168.4.1/api/sensors`
3. **Live data** → Updates water level and air quality in real-time
4. **Color-coded** → Visual indicators change based on values
5. **Status** → Green pulsing dot shows connection status

## ESP32 API Endpoint

The app fetches from:
```
GET http://192.168.4.1/api/sensors
```

Response (JSON):
```json
{
  "ir": false,           // Motion: true/false
  "flame": false,        // Fire: true/false
  "gas": false,          // Gas: true/false
  "water": 45.5,         // Water level: 0-100%
  "mq2_rating": 3,       // Air quality: 1-10
  "buzzer": false,       // Buzzer active
  "muted": false,        // Buzzer muted
  "raw_water": 2500      // Raw analog value
}
```

## Troubleshooting

### App shows "Not connected"
- Check you're connected to `HATSS_SECURITY_NET` WiFi
- Verify ESP32 is powered on
- Check Serial Monitor for errors
- Try refreshing app (Ctrl+R)

### Water level shows 0%
- Check water sensor is connected to GPIO 34
- Verify sensor is getting power
- Check for loose connections
- Restart ESP32

### Air quality shows 0
- Check MQ2 sensor is connected to GPIO 33
- Verify sensor is powered
- MQ2 takes ~60 seconds to warm up after power
- Check Serial Monitor for sensor errors

### Updates not refreshing
- Ensure WiFi connection is stable
- Check no firewall blocking port 80
- Try hard refresh (Ctrl+Shift+R)
- Restart ESP32

### Can't connect to WiFi hotspot
- Verify ESP32 is running (green LED should be on)
- Check WiFi name is exactly `HATSS_SECURITY_NET`
- Try password: `HATSS1234` (case sensitive)
- Move closer to ESP32
- Restart WiFi on your device

## Features at a Glance

✅ Real-time sensor data from ESP32  
✅ Live water level indicator (0-100%)  
✅ Live air quality gauge (1-10 scale)  
✅ Color-coded status badges  
✅ Smooth animated bars  
✅ 4 sensor alert cards  
✅ Automatic updates every 1 second  
✅ Connected status indicator  
✅ IP address display  
✅ Last update timestamp  
✅ Threshold markers  
✅ Quality legend  
✅ Alert warnings  

## Next Steps

1. ✅ Upload ESP32 code
2. ✅ Power on ESP32
3. ✅ Connect to `HATSS_SECURITY_NET`
4. ✅ Open app at `http://localhost:5173`
5. ✅ Go to Sensors page
6. ✅ Watch live water level and air quality update
7. ✅ Test by interacting with sensors (pour water, light fire sensor, etc.)

---

**Note:** Both app and ESP32 must be on the same network for this to work!
