import { useEffect, useState } from 'react';

interface SensorMonitorProps {
  theme: 'light' | 'dark';
}

interface SensorState {
  fire: boolean;
  pir: boolean;
  gas: boolean;
  last_update: string;
}

export function SensorMonitor({ theme }: SensorMonitorProps) {
  const [sensors, setSensors] = useState<SensorState>({
    fire: false,
    pir: false,
    gas: false,
    last_update: 'Not received',
  });

  useEffect(() => {
    const fetchSensors = async () => {
      try {
        const res = await fetch('/api/v1/sensors/status');
        const data = await res.json();
        setSensors(data);
      } catch (error) {
        console.error('Sensor status error:', error);
      }
    };

    fetchSensors();
    const interval = setInterval(fetchSensors, 1000);
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

  return (
    <div className="space-y-4">
      <div className={`${bgColor} rounded-lg border ${borderColor} p-4`}>
        <p className="text-xs text-slate-500">Last Update: {sensors.last_update}</p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <Sensor icon="🔥" name="Fire" active={sensors.fire} />
        <Sensor icon="👁️" name="Motion" active={sensors.pir} />
        <Sensor icon="🛢️" name="Gas" active={sensors.gas} />
      </div>
    </div>
  );
}
