import { useCallback, useEffect, useState, type FormEvent } from 'react';

import { DashboardPanel } from './components/DashboardPanel';
import { DeviceTable, type Device } from './components/DeviceTable';
import { MetricCard } from './components/MetricCard';
import { Sidebar } from './components/Sidebar';
import { SystemHealth } from './components/SystemHealth';
import { FaceMonitor } from './components/FaceMonitor';
import { SensorMonitor } from './components/SensorMonitor';
import { IntrusionGallery } from './components/IntrusionGallery';

import {
  getCopilotStatus,
  getDefenderScanCapability,
  getDefenderOverview,
  getNetworkOverview,
  getSystemOverview,
  getSysmonOverview,
  requestCopilotBrief,
  startDefenderScan,
  type CopilotBrief,
  type CopilotStatus,
  type DefenderScanCapability,
  type DefenderOverview,
  type DefenderScanAction,
  type NetworkOverview,
  type SysmonOverview,
  type SystemOverview,
} from './services/api';

const refreshMs = 10_000;
type AppRoute = '#overview' | '#security' | '#processes' | '#network' | '#files' | '#copilot' | '#face' | '#sensors';
type ThemeMode = 'light' | 'dark';
const routes: AppRoute[] = [
  '#overview',
  '#security',
  '#processes',
  '#network',
  '#files',
  '#copilot',
  '#face',
  '#sensors',
];

function currentRoute(): AppRoute {
  return routes.includes(window.location.hash as AppRoute)
    ? (window.location.hash as AppRoute)
    : '#overview';
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ['KB', 'MB', 'GB', 'TB'];
  const unit = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length);
  return `${(bytes / 1024 ** unit).toFixed(unit > 1 ? 1 : 0)} ${units[unit - 1]}`;
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86_400);
  const hours = Math.floor((seconds % 86_400) / 3_600);
  return days ? `${days}d ${hours}h` : `${hours}h`;
}

function statusForPercent(percent: number): string {
  if (percent >= 90) return 'High usage';
  if (percent >= 75) return 'Elevated';
  return 'Within range';
}

function toProcessRows(overview: SystemOverview): Device[] {
  return overview.top_processes.map((process) => ({
    activity: `${process.memory_percent.toFixed(1)}% memory`,
    name: process.name,
    status: process.status,
    type: `PID ${process.pid}`,
  }));
}

function SourceState({
  source,
  detail,
  available,
}: {
  source: string;
  detail: string;
  available: boolean;
}) {
  return (
    <>
      <p className={available ? 'text-emerald-700' : 'text-amber-700'}>
        {source}: {available ? 'source connected' : 'source unavailable'}
      </p>
      <p>{detail}</p>
    </>
  );
}

function getInitialTheme(): ThemeMode {
  if (typeof window === 'undefined') return 'dark';
  const savedTheme = window.localStorage.getItem('hatss-theme');
  if (savedTheme === 'dark' || savedTheme === 'light') return savedTheme;
  return 'dark';
}

export function App() {
  const [route, setRoute] = useState<AppRoute>(currentRoute);
  const [theme, setTheme] = useState<ThemeMode>(getInitialTheme);
  const [overview, setOverview] = useState<SystemOverview | null>(null);
  const [defender, setDefender] = useState<DefenderOverview | null>(null);
  const [sysmon, setSysmon] = useState<SysmonOverview | null>(null);
  const [network, setNetwork] = useState<NetworkOverview | null>(null);
  const [scanCapability, setScanCapability] = useState<DefenderScanCapability | null>(null);
  const [copilotStatus, setCopilotStatus] = useState<CopilotStatus | null>(null);
  const [scanDirectory, setScanDirectory] = useState('');
  const [scanAction, setScanAction] = useState<DefenderScanAction | null>(null);
  const [scanError, setScanError] = useState<string | null>(null);
  const [isStartingScan, setIsStartingScan] = useState(false);
  const [copilotQuestion, setCopilotQuestion] = useState(
    'Summarize the current security evidence.',
  );
  const [copilotBrief, setCopilotBrief] = useState<CopilotBrief | null>(null);
  const [copilotError, setCopilotError] = useState<string | null>(null);
  const [isRequestingBrief, setIsRequestingBrief] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadOverview = useCallback(async (signal?: AbortSignal) => {
    try {
      const [
        nextOverview,
        nextDefender,
        nextSysmon,
        nextNetwork,
        nextScanCapability,
        nextCopilotStatus,
      ] = await Promise.all([
        getSystemOverview(signal),
        getDefenderOverview(signal),
        getSysmonOverview(signal),
        getNetworkOverview(signal),
        getDefenderScanCapability(signal),
        getCopilotStatus(signal),
      ]);
      setOverview(nextOverview);
      setDefender(nextDefender);
      setSysmon(nextSysmon);
      setNetwork(nextNetwork);
      setScanCapability(nextScanCapability);
      setCopilotStatus(nextCopilotStatus);
      setError(null);
    } catch (requestError) {
      if (requestError instanceof DOMException && requestError.name === 'AbortError') return;
      setError('Live telemetry is unavailable. Start the HATSS API and refresh this page.');
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, []);

  async function handleStartScan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsStartingScan(true);
    setScanError(null);
    setScanAction(null);
    try {
      setScanAction(await startDefenderScan(scanDirectory));
    } catch (requestError) {
      setScanError(
        requestError instanceof Error ? requestError.message : 'Unable to start the scan.',
      );
    } finally {
      setIsStartingScan(false);
    }
  }

  async function handleCopilotBrief(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsRequestingBrief(true);
    setCopilotError(null);
    setCopilotBrief(null);
    try {
      setCopilotBrief(await requestCopilotBrief(copilotQuestion));
    } catch (requestError) {
      setCopilotError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to request a local AI briefing.',
      );
    } finally {
      setIsRequestingBrief(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadOverview(controller.signal);
    const intervalId = window.setInterval(() => void loadOverview(), refreshMs);
    return () => {
      controller.abort();
      window.clearInterval(intervalId);
    };
  }, [loadOverview]);

  useEffect(() => {
    const onHashChange = () => setRoute(currentRoute());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem('hatss-theme', theme);
  }, [theme]);

  const metrics = overview
    ? [
        {
          change: `${overview.cpu.logical_cores} logical cores`,
          label: 'CPU usage',
          tone: 'blue' as const,
          value: `${overview.cpu.usage_percent.toFixed(0)}%`,
        },
        {
          change: `${formatBytes(overview.memory.available_bytes)} available`,
          label: 'Memory usage',
          tone: 'violet' as const,
          value: `${overview.memory.usage_percent.toFixed(0)}%`,
        },
        {
          change: `${formatBytes(overview.disk.free_bytes)} free`,
          label: 'System disk',
          tone: 'emerald' as const,
          value: `${overview.disk.usage_percent.toFixed(0)}%`,
        },
        {
          change:
            overview.process_collection_status === 'available'
              ? 'Accessible processes'
              : 'Collection limited',
          label: 'Running processes',
          tone: 'amber' as const,
          value:
            overview.process_collection_status === 'available'
              ? overview.running_processes.toString()
              : '—',
        },
      ]
    : [];

  const healthItems = overview
    ? [
        {
          label: 'CPU usage',
          status: statusForPercent(overview.cpu.usage_percent),
          value: `${overview.cpu.usage_percent.toFixed(1)}%`,
          valuePercent: overview.cpu.usage_percent,
        },
        {
          label: 'Memory usage',
          status: statusForPercent(overview.memory.usage_percent),
          value: `${overview.memory.usage_percent.toFixed(1)}%`,
          valuePercent: overview.memory.usage_percent,
        },
        {
          label: 'System disk usage',
          status: statusForPercent(overview.disk.usage_percent),
          value: `${overview.disk.usage_percent.toFixed(1)}%`,
          valuePercent: overview.disk.usage_percent,
        },
      ]
    : [];

  const pageTitles: Record<AppRoute, [string, string]> = {
    '#overview': [
      'Live system overview',
      'Read-only operational telemetry from the machine running the HATSS API. Refreshes every 10 seconds.',
    ],
    '#security': [
      'Security center',
      'Evidence reported by Microsoft Defender and Sysmon. HATSS does not invent threat verdicts.',
    ],
    '#processes': [
      'Processes',
      'Accessible processes ranked by current memory share. Process presence alone is not suspicious.',
    ],
    '#network': [
      'Network Manager',
      'Live Windows neighbor and TCP connection facts; no network scanning or threat labels.',
    ],
    '#files': [
      'File security',
      'Start one explicit Microsoft Defender custom scan for a folder you select.',
    ],
    '#copilot': [
      'AI copilot',
      'A local Ollama model can explain bounded HATSS evidence after your consent.',
    ],
    '#face': [
      'Face Recognition',
      'Real-time face detection and intrusion alerts from connected cameras.',
    ],
    '#sensors': [
      'Sensor Monitoring',
      'ESP32 multi-sensor monitoring including fire, motion, and gas detection.',
    ],
  };
  const [title, description] = pageTitles[route];

  // Face page
  const facePage = (
    <>
      <section className="mt-7 grid gap-7 xl:grid-cols-2">
        <DashboardPanel title="Face Recognition" description={description} theme={theme}>
          <FaceMonitor theme={theme} />
        </DashboardPanel>
        <DashboardPanel title="Intrusion Alerts" description="Recent intrusion captures" theme={theme}>
          <IntrusionGallery theme={theme} />
        </DashboardPanel>
      </section>
    </>
  );

  // Sensors page
  const sensorsPage = (
    <>
      <section className="mt-7 grid gap-7 xl:grid-cols-2">
        <DashboardPanel title="ESP32 Sensors" description={description} theme={theme}>
          <SensorMonitor theme={theme} />
        </DashboardPanel>
        <DashboardPanel title="Sensor Metrics" description="Sensor summary and alerts" theme={theme}>
          <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-slate-800' : 'bg-slate-100'}`}>
            <p className="text-sm text-slate-600">Sensor data updates every 1 second</p>
            <p className="text-xs text-slate-500 mt-2">
              Fire, motion, and gas sensors are monitored in real-time for threat detection.
            </p>
          </div>
        </DashboardPanel>
      </section>
    </>
  );

  const page =
    route === '#overview'
      ? 'overview'
      : route === '#security'
        ? 'security'
        : route === '#processes'
          ? 'processes'
          : route === '#network'
            ? 'network'
            : route === '#files'
              ? 'files'
              : route === '#copilot'
                ? 'copilot'
                : route === '#face'
                  ? 'face'
                  : 'sensors';

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-slate-950 text-white' : 'bg-white text-slate-900'}`}>
      <div className="flex">
        <Sidebar
          currentRoute={route}
          theme={theme}
          onThemeChange={setTheme}
          onNavigate={(hash) => {
            window.location.hash = hash;
            setRoute(hash as AppRoute);
          }}
        />

        <main className="flex-1 overflow-auto">
          <header className={`${theme === 'dark' ? 'bg-slate-900' : 'bg-slate-100'} border-b ${theme === 'dark' ? 'border-slate-800' : 'border-slate-200'} sticky top-0 z-10 px-8 py-4`}>
            <h1 className="text-3xl font-bold">{title}</h1>
            <p className="text-sm mt-1 text-slate-500">{description}</p>
          </header>

          <div className="p-8">
            {error && (
              <div className="rounded-lg bg-red-50 p-4 text-red-800 mb-6">
                <p>{error}</p>
              </div>
            )}

            {loading && page === 'overview' && (
              <div className="text-center py-8">
                <p className="text-slate-500">Loading telemetry...</p>
              </div>
            )}

            {page === 'face' && facePage}
            {page === 'sensors' && sensorsPage}
          </div>
        </main>
      </div>
    </div>
  );
}
