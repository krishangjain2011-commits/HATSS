# Simple HTTP GET Request from ESP32

## What Changed

**Before:** Complex fetch with CORS headers
```javascript
fetch(`http://192.168.4.1/api/sensors`, {
  signal: controller.signal,
  mode: 'cors',
  headers: {
    'Accept': 'application/json',
  },
})
```

**Now:** Simple HTTP GET request (no CORS needed)
```javascript
fetch('http://192.168.4.1/api/sensors', {
  method: 'GET',
})
```

## How It Works

1. **Browser sends HTTP GET request** to `http://192.168.4.1/api/sensors`
2. **ESP32 receives request** and sends JSON response
3. **App parses JSON** and updates UI with sensor data
4. **Every 1 second** the request repeats for live updates

## Data Flow

```
App (localhost:5173)
    ↓
HTTP GET http://192.168.4.1/api/sensors
    ↓
ESP32 (192.168.4.1)
    ↓
Returns JSON:
{
  "fire": false,
  "pir": false,
  "gas": false,
  "water": 45.5,
  "mq2_rating": 3,
  "buzzer": false,
  "muted": false,
  "raw_water": 2500
}
    ↓
App displays:
- Water Level: 45.5%
- Air Quality: 3/10
- Sensor Alerts
```

## Step by Step

1. **Connect to ESP32 hotspot**
   - WiFi: `HATSS_SECURITY_NET`
   - Password: `HATSS1234`

2. **Open app**
   - URL: `http://localhost:5173`
   - Navigate to Sensors page

3. **App makes HTTP GET request**
   ```
   GET http://192.168.4.1/api/sensors
   ```

4. **ESP32 responds with JSON**
   - HTTP 200 OK
   - Content-Type: application/json
   - Body: sensor data

5. **App updates UI**
   - Water level indicator fills
   - Air quality bar shows rating
   - Sensor cards show alerts
   - Last update timestamp updates

## Logging

Open browser console (F12) to see:
- 🔍 HTTP GET from ESP32: http://192.168.4.1/api/sensors
- ✓ HTTP Response: 200
- ✓ Data from ESP32: {...json...}
- ✓ UI Updated with ESP32 data

## If It Still Doesn't Work

**Check the browser console for error messages:**
- `ERR_CONNECTION_REFUSED` → ESP32 not running or wrong IP
- `ERR_NAME_NOT_RESOLVED` → 192.168.4.1 not found (not on WiFi?)
- `ERR_BLOCKED_BY_CLIENT` → Browser extension blocking
- `404 Not Found` → Wrong endpoint on ESP32

**Check these:**
1. Are you connected to `HATSS_SECURITY_NET`?
2. Is ESP32 powered on?
3. Does Serial Monitor show "WiFi AP started"?
4. Is backend running? (fallback mode)
5. Check firewall isn't blocking port 80

## Benefits of Simple HTTP GET

✅ No CORS needed  
✅ Simple and straightforward  
✅ Works from any origin  
✅ Faster response  
✅ Less overhead  
✅ Standard HTTP method  

## Testing

Test manually from browser console:
```javascript
fetch('http://192.168.4.1/api/sensors')
  .then(r => r.json())
  .then(d => console.log(d))
  .catch(e => console.error(e))
```

If this works in console, it will work in the app!
