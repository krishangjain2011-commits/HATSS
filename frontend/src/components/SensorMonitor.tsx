import { useEffect, useState } from 'react';

interface SensorMonitorProps {
  theme: 'light' | 'dark';
}

interface SensorState {
  fire: boolean;
  pir: boolean;
  gas: boolean;
  water_level: number;
  water_level_alert: boolean;
  last_update: string;
  source?: 'backend' | 'esp32';
  mq2_rating?: number;
  mq2_ppm?: number; // Raw PPM value from MQ2 sensor
}

export function SensorMonitor({ theme }: SensorMonitorProps) {
  const [sensors, setSensors] = useState<SensorState>({
    fire: false,
    pir: false,
    gas: false,
    water_level: 0,
    water_level_alert: false,
    last_update: 'Not received',
    source: undefined,
    mq2_rating: 0,
    mq2_ppm: 0,
  });

  const [esp32Status, setEsp32Status] = useState<'connected' | 'disconnected'>('disconnected');

  useEffect(() => {
    const fetchSensors = async () => {
      try {
        // Primary: Try ESP32 directly (fastest path)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 500);
        
        const response = await fetch('http://192.168.4.1/api/sensors', {
          method: 'GET',
          mode: 'cors',
          credentials: 'omit',
          signal: controller.signal,
        }).finally(() => clearTimeout(timeoutId));

        if (response.status === 200) {
          const data = await response.json();
          setEsp32Status('connected');

          setSensors({
            fire: data.flame === true,
            pir: data.ir === true,
            gas: data.gas === true,
            water_level: parseFloat(data.water) || 0,
            water_level_alert: (parseFloat(data.water) || 0) > 75,
            mq2_rating: parseInt(data.mq2_rating) || 0,
            mq2_ppm: parseFloat(data.mq2_ppm) || 0,
            last_update: new Date().toLocaleTimeString(),
            source: 'esp32',
          });
          return;
        }
      } catch (error) {
        // Continue to fallback
      }

      try {
        // Fallback: Try backend proxy
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 500);
        
        const response = await fetch('/api/v1/sensors/esp32/live', {
          signal: controller.signal,
        }).finally(() => clearTimeout(timeoutId));

        if (response.status === 200) {
          const data = await response.json();
          setEsp32Status('connected');

          setSensors({
            fire: data.fire === true,
            pir: data.pir === true,
            gas: data.gas === true,
            water_level: parseFloat(data.water_level) || 0,
            water_level_alert: (parseFloat(data.water_level) || 0) > 75,
            mq2_rating: parseInt(data.mq2_rating) || 0,
            mq2_ppm: parseFloat(data.mq2_ppm) || 0,
            last_update: new Date().toLocaleTimeString(),
            source: 'esp32',
          });
          return;
        }
      } catch (error) {
        // Continue to final fallback
      }

      // Final fallback: Stored backend data
      try {
        setEsp32Status('disconnected');
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 500);
        
        const response = await fetch('/api/v1/sensors/status', {
          signal: controller.signal,
        }).finally(() => clearTimeout(timeoutId));
        
        const data = await response.json();
        setSensors({
          ...data,
          source: 'backend',
          mq2_rating: data.mq2_rating || 0,
          mq2_ppm: data.mq2_ppm || 0,
        });
      } catch (error) {
        // Silent fail
      }
    };

    fetchSensors();
    const interval = setInterval(fetchSensors, 5);
    return () => clearInterval(interval);
  }, []);

  const bgColor = theme === 'dark' ? 'bg-slate-950' : 'bg-white';
  const textColor = theme === 'dark' ? 'text-white' : 'text-slate-900';
  const borderColor = theme === 'dark' ? 'border-slate-700' : 'border-slate-300';

  const Sensor = ({ icon, name, active }: { icon: string; name: string; active: boolean }) => (
    <div
      className={`${bgColor} rounded-xl border transition-all ${
        active ? 'border-red-500 bg-red-500/5 shadow-lg shadow-red-500/20' : `border-${borderColor}`
      } p-4`}
    >
      <div className="flex items-center justify-between">
        <div className="text-2xl">{icon}</div>
        <div
          className={`w-3 h-3 rounded-full ${
            active ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'
          }`}
        />
      </div>
      <p className={`text-xs font-medium mt-2 ${active ? 'text-red-500' : 'text-emerald-600'} uppercase`}>
        {name}
      </p>
      <p className={`text-sm font-bold mt-1 ${textColor}`}>{active ? 'ALERT' : 'CLEAR'}</p>
    </div>
  );

  // Get air quality text and color based on MQ2 rating
  const getAirQualityInfo = (rating: number) => {
    if (rating <= 2) return { text: 'EXCELLENT', color: '#10b981', bgColor: 'bg-emerald-500/10' };
    if (rating <= 4) return { text: 'GOOD', color: '#3b82f6', bgColor: 'bg-blue-500/10' };
    if (rating <= 6) return { text: 'MODERATE', color: '#f59e0b', bgColor: 'bg-yellow-500/10' };
    if (rating <= 8) return { text: 'POOR', color: '#f97316', bgColor: 'bg-orange-500/10' };
    return { text: 'HAZARDOUS', color: '#ef4444', bgColor: 'bg-red-500/10' };
  };

  const airQuality = getAirQualityInfo(sensors.mq2_rating || 0);

  // Get water level status
  const getWaterLevelStatus = (level: number) => {
    if (level < 20) return { status: 'LOW', color: '#3b82f6' };
    if (level < 50) return { status: 'MEDIUM', color: '#f59e0b' };
    if (level < 75) return { status: 'HIGH', color: '#f97316' };
    return { status: 'CRITICAL', color: '#ef4444' };
  };

  const waterStatus = getWaterLevelStatus(sensors.water_level);

  return (
    <div className="space-y-4">
      {/* Status Header */}
      <div className={`${bgColor} rounded-lg border ${borderColor} p-4`}>
        <div className="flex justify-between items-center">
          <div>
            <p className="text-xs text-slate-500">Last Update: {sensors.last_update}</p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                esp32Status === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'
              }`}
            />
            <span className="text-xs text-slate-500">
              Connected to: <span className="font-semibold">192.168.4.1 (ESP32)</span>
            </span>
          </div>
        </div>
      </div>

      {/* Sensor Alert Cards */}
      <div className="grid grid-cols-4 gap-3">
        <Sensor icon="🔥" name="Fire" active={sensors.fire} />
        <Sensor icon="👁️" name="Motion" active={sensors.pir} />
        <Sensor icon="🛢️" name="Gas" active={sensors.gas} />
        <Sensor icon="💧" name="Water" active={sensors.water_level_alert} />
      </div>

      {/* Live Water Level Indicator */}
      <div className={`${bgColor} rounded-lg border ${borderColor} p-4`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">💧</span>
            <p className="text-sm font-medium text-slate-600">Live Water Level</p>
          </div>
          <span className="text-xs font-semibold px-2 py-1 rounded" style={{ color: waterStatus.color, backgroundColor: `${waterStatus.color}20` }}>
            {waterStatus.status}
          </span>
        </div>

        {/* Water Level Percentage */}
        <div className="mb-3">
          <div className="flex justify-between items-baseline mb-2">
            <span className="text-2xl font-bold" style={{ color: waterStatus.color }}>
              {sensors.water_level.toFixed(1)}%
            </span>
            <span className="text-xs text-slate-500">Max Capacity</span>
          </div>

          {/* Water Level Bar */}
          <div className={`w-full h-4 rounded-full overflow-hidden ${theme === 'dark' ? 'bg-slate-800' : 'bg-slate-200'}`}>
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{
                width: `${Math.min(sensors.water_level, 100)}%`,
                background: `linear-gradient(90deg, ${waterStatus.color}, ${waterStatus.color}dd)`,
              }}
            />
          </div>
        </div>

        {/* Water Level Threshold Markers */}
        <div className="flex justify-between text-xs text-slate-500 mb-3">
          <span>0%</span>
          <span>25%</span>
          <span>50%</span>
          <span>75%</span>
          <span>100%</span>
        </div>

        {/* Water Level Warning */}
        {sensors.water_level_alert && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-2">
            <p className="text-xs text-red-600 font-semibold">⚠️ HIGH WATER LEVEL - EXCEEDS 75% CAPACITY</p>
          </div>
        )}
      </div>

      {/* Live Air Quality Indicator */}
      <div className={`${bgColor} rounded-lg border ${borderColor} p-4`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">💨</span>
            <p className="text-sm font-medium text-slate-600">Live Air Quality</p>
          </div>
          <span className="text-xs font-semibold px-2 py-1 rounded" style={{ color: airQuality.color, backgroundColor: `${airQuality.color}20` }}>
            {airQuality.text}
          </span>
        </div>

        {/* Air Quality Rating */}
        <div className="mb-3">
          <div className="flex justify-between items-baseline mb-2">
            <span className="text-2xl font-bold" style={{ color: airQuality.color }}>
              {sensors.mq2_rating}/10
            </span>
            <span className="text-xs text-slate-500">Rating Scale</span>
          </div>

          {/* Air Quality Bar */}
          <div className={`w-full h-4 rounded-full overflow-hidden ${theme === 'dark' ? 'bg-slate-800' : 'bg-slate-200'}`}>
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{
                width: `${(sensors.mq2_rating || 0) * 10}%`,
                background: `linear-gradient(90deg, ${airQuality.color}, ${airQuality.color}dd)`,
              }}
            />
          </div>
        </div>

        {/* MQ2 PPM Value (if available from ESP32) */}
        {sensors.mq2_ppm !== undefined && sensors.mq2_ppm > 0 && (
          <div className="mb-3 p-2 rounded bg-slate-100 dark:bg-slate-800">
            <div className="flex justify-between items-center">
              <span className="text-xs text-slate-600">MQ2 Sensor PPM:</span>
              <span className="text-sm font-semibold" style={{ color: airQuality.color }}>
                {sensors.mq2_ppm.toFixed(1)} PPM
              </span>
            </div>
          </div>
        )}

        {/* Air Quality Scale */}
        <div className="flex justify-between text-xs text-slate-500 mb-3">
          <span>0</span>
          <span>2.5</span>
          <span>5</span>
          <span>7.5</span>
          <span>10</span>
        </div>

        {/* Air Quality Legend */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-slate-500">0-2: Excellent</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-slate-500">2-4: Good</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-500" />
            <span className="text-slate-500">4-6: Moderate</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-slate-500">6+: Poor/Hazard</span>
          </div>
        </div>

        {/* Gas Alert */}
        {sensors.gas && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-2 mt-3">
            <p className="text-xs text-red-600 font-semibold">🚨 GAS DETECTED - AIR QUALITY HAZARDOUS</p>
          </div>
        )}
      </div>

      {/* Standard Water Level Gauge (Compact) */}
      <div className={`${bgColor} rounded-lg border ${borderColor} p-4`}>
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-slate-600">Water Level (Gauge)</p>
          <span className={`text-lg font-bold ${sensors.water_level_alert ? 'text-red-600' : 'text-blue-600'}`}>
            {sensors.water_level.toFixed(1)}%
          </span>
        </div>
        <div className={`w-full h-2 rounded-full ${theme === 'dark' ? 'bg-slate-800' : 'bg-slate-200'}`}>
          <div
            className={`h-full rounded-full transition-all ${
              sensors.water_level > 75
                ? 'bg-red-500'
                : sensors.water_level > 50
                  ? 'bg-yellow-500'
                  : 'bg-blue-500'
            }`}
            style={{ width: `${Math.min(sensors.water_level, 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-slate-500 mt-1">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  );
}
