import { useCallback, useEffect, useState, type FormEvent } from 'react';

import { DashboardPanel } from './components/DashboardPanel';
import { DeviceTable, type Device } from './components/DeviceTable';
import { FaceMonitor } from './components/FaceMonitor';
import { IntrusionGallery } from './components/IntrusionGallery';
import { MetricCard } from './components/MetricCard';
import { SensorMonitor } from './components/SensorMonitor';
import { Sidebar } from './components/Sidebar';
import { SystemHealth } from './components/SystemHealth';
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
type AppRoute = '#overview' | '#security' | '#processes' | '#network' | '#files' | '#face' | '#sensors' | '#copilot';
type ThemeMode = 'light' | 'dark';
const routes: AppRoute[] = [
  '#overview',
  '#security',
  '#processes',
  '#network',
  '#files',
  '#face',
  '#sensors',
  '#copilot',
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
    '#face': [
      'Face recognition',
      'Real-time face detection, known person identification, and intrusion capture gallery.',
    ],
    '#sensors': [
      'Sensors',
      'ESP32 sensor status including fire detection, motion/PIR, and gas detection.',
    ],
    '#copilot': [
      'AI copilot',
      'A local Ollama model can explain bounded HATSS evidence after your consent.',
    ],
  };
  const [title, description] = pageTitles[route];

  const overviewPage = overview && (
    <>
      <section
        aria-label="Live system metrics"
        className="mt-7 grid gap-4 sm:grid-cols-2 2xl:grid-cols-4"
      >
        {metrics.map((metric) => (
          <MetricCard {...metric} key={metric.label} theme={theme} />
        ))}
      </section>
      <section className="mt-7 grid gap-7 xl:grid-cols-[1.4fr_1fr]">
        <DashboardPanel
          description="Facts observed from the host. HATSS has not made a threat verdict or security score."
          theme={theme}
          title="Monitoring boundary"
        >
          <div className="space-y-5 text-sm leading-6 text-slate-600">
            <p>
              <span className="font-medium text-slate-900">Host:</span> {overview.host.hostname} ·{' '}
              {overview.host.operating_system}
            </p>
            <p>
              <span className="font-medium text-slate-900">Uptime:</span>{' '}
              {formatUptime(overview.host.uptime_seconds)} · booted{' '}
              {new Date(overview.host.booted_at).toLocaleString()}
            </p>
            <div className="rounded-2xl border border-slate-800 bg-slate-950/95 p-4 shadow-sm">
              <p className="font-medium text-white">What this does now</p>
              <p className="mt-1 text-slate-300">
                Reads CPU, memory, disk, and accessible process metadata. It does not scan files,
                inspect network traffic, identify malware, or change anything on your device.
              </p>
            </div>
          </div>
        </DashboardPanel>
        <DashboardPanel
          description="Current measurements, not a security assessment."
          theme={theme}
          title="System health"
        >
          <SystemHealth items={healthItems} theme={theme} />
        </DashboardPanel>
      </section>
      <section className="mt-7 grid gap-7 xl:grid-cols-2">
        <DashboardPanel
          description="A direct summary of the Microsoft Defender source."
          theme={theme}
          title="Defender summary"
        >
          {defender ? (
            <div className="space-y-3 text-sm leading-6 text-slate-600">
              <SourceState
                available={defender.state.status === 'available'}
                detail={defender.state.detail}
                source="Microsoft Defender"
              />
              <p>
                Historical detection records returned:{' '}
                <span className="font-medium text-slate-900">{defender.detections.length}</span>
              </p>
              <a className="inline-flex text-fuchsia-600 underline underline-offset-4 transition hover:text-fuchsia-700" href="#security">
                View detection evidence
              </a>
            </div>
          ) : (
            <p className="text-sm text-slate-600">Reading Defender status…</p>
          )}
        </DashboardPanel>
        <DashboardPanel
          description="A direct summary of the Sysmon event-log source."
          theme={theme}
          title="Sysmon summary"
        >
          {sysmon ? (
            <div className="space-y-3 text-sm leading-6 text-slate-600">
              <SourceState
                available={sysmon.state.status === 'available'}
                detail={sysmon.state.detail}
                source="Sysmon"
              />
              <p>
                Recent events returned:{' '}
                <span className="font-medium text-slate-900">{sysmon.events.length}</span>
              </p>
              <a className="inline-flex text-fuchsia-600 underline underline-offset-4 transition hover:text-fuchsia-700" href="#security">
                View event evidence
              </a>
            </div>
          ) : (
            <p className="text-sm text-slate-600">Reading Sysmon events…</p>
          )}
        </DashboardPanel>
      </section>
    </>
  );

  const securityPage = (
    <section className="mt-7 grid gap-7 xl:grid-cols-2">
      <DashboardPanel
        description="Read directly from the Microsoft Defender engine. HATSS displays its records and does not reinterpret them."
        theme={theme}
        title="Microsoft Defender evidence"
      >
        {defender ? (
          <div className="space-y-4 text-sm leading-6 text-slate-600">
            <SourceState
              available={defender.state.status === 'available'}
              detail={defender.state.detail}
              source="Microsoft Defender"
            />
            {defender.state.status === 'available' && (
              <p>
                Antivirus: {String(defender.antivirus_enabled)} · real-time protection:{' '}
                {String(defender.real_time_protection_enabled)} · behavior monitoring:{' '}
                {String(defender.behavior_monitor_enabled)}
              </p>
            )}
            <div className="rounded-2xl border border-slate-800 bg-slate-950/95 p-4 shadow-sm">
              <p className="font-medium text-white">
                Historical detection records returned: {defender.detections.length}
              </p>
              {defender.detections.length ? (
                <ul className="mt-3 max-h-80 space-y-3 overflow-y-auto">
                  {defender.detections.map((detection, index) => (
                    <li key={`${detection.threat_id}-${detection.detected_at}-${index}`}>
                      <span className="font-medium text-white">{detection.name}</span>
                      {detection.severity ? ` · severity: ${detection.severity}` : ''}
                      {detection.detected_at
                        ? ` · ${new Date(detection.detected_at).toLocaleString()}`
                        : ''}
                      <p className="text-xs text-slate-400">
                        Defender action succeeded:{' '}
                        {detection.action_success === null
                          ? 'not reported'
                          : String(detection.action_success)}
                      </p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-2 text-slate-500">
                  No historical detection records were returned by Defender.
                </p>
              )}
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-600">Reading Defender status…</p>
        )}
      </DashboardPanel>
      <DashboardPanel
        description="Events collected by Sysmon and read from its Windows event log. They are evidence, not HATSS threat verdicts."
        theme={theme}
        title="Sysmon evidence"
      >
        {sysmon ? (
          <div className="space-y-4 text-sm leading-6 text-slate-600">
            <SourceState
              available={sysmon.state.status === 'available'}
              detail={sysmon.state.detail}
              source="Sysmon"
            />
            <p>
              Recent Sysmon events returned:{' '}
              <span className="font-medium text-slate-900">{sysmon.events.length}</span>
            </p>
            {sysmon.events.length ? (
              <ul className="max-h-80 space-y-3 overflow-y-auto border-t border-slate-800 pt-3">
                {sysmon.events.map((event) => (
                  <li key={event.record_id}>
                    <span className="font-medium text-slate-900">
                      Event {event.event_id}: {event.event_type}
                    </span>{' '}
                    ·{' '}
                    {new Date(event.occurred_at).toLocaleString()}
                    <p className="mt-0.5 line-clamp-3 text-xs text-slate-500">{event.message}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-slate-500">No recent events were returned by Sysmon.</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-slate-600">Reading Sysmon events…</p>
        )}
      </DashboardPanel>
    </section>
  );

  const processesPage = overview && (
    <section className="mt-7">
      <DashboardPanel
        description="Top accessible processes ranked by current memory share. Process presence alone is not suspicious."
        theme={theme}
        title="Running processes"
      >
        {overview.process_collection_status === 'available' ? (
          <DeviceTable devices={toProcessRows(overview)} theme={theme} />
        ) : (
          <p className="text-sm leading-6 text-slate-600">
            Process details are not accessible to this HATSS instance. No process count or verdict
            is being shown.
          </p>
        )}
      </DashboardPanel>
    </section>
  );

  const networkPage = (
    <section className="mt-7 grid gap-7 xl:grid-cols-2">
      <DashboardPanel
        description="Neighbor entries reported by the local Windows networking stack. This does not probe devices."
        theme={theme}
        title="Known network neighbors"
      >
        {network ? (
          <div className="space-y-4 text-sm leading-6 text-slate-600">
            <SourceState
              available={network.state.status === 'available'}
              detail={network.state.detail}
              source="Windows networking"
            />
            <button
              className="rounded-2xl border border-slate-700 bg-slate-950 px-3 py-2 text-left text-sm font-medium text-white transition hover:-translate-y-0.5 hover:shadow-lg hover:bg-slate-900"
              onClick={() => {
                setCopilotQuestion(
                  'Explain the IP addresses, ports, TCP states, interface names, MAC addresses, and process IDs shown on the Network page. Tell me what each means and what would be worth reviewing, without calling anything malicious without evidence.',
                );
                window.location.hash = '#copilot';
              }}
              type="button"
            >
              Ask copilot to explain these network fields
            </button>
            <p>
              Neighbor entries returned:{' '}
              <span className="font-medium text-slate-900">{network.neighbors.length}</span>
            </p>
            {network.neighbors.length ? (
              <ul className="max-h-96 space-y-3 overflow-y-auto border-t border-slate-800 pt-3">
                {network.neighbors.map((neighbor) => (
                  <li key={`${neighbor.interface_alias}-${neighbor.ip_address}`}>
                    <p className="font-mono text-xs text-slate-900">{neighbor.ip_address}</p>
                    <p className="text-xs text-slate-500">
                      {neighbor.interface_alias || 'Unknown interface'} ·{' '}
                      {neighbor.state || 'Unknown state'}
                      {neighbor.link_layer_address ? ` · ${neighbor.link_layer_address}` : ''}
                    </p>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : (
          <p className="text-sm text-slate-600">Reading Windows network data…</p>
        )}
      </DashboardPanel>
      <DashboardPanel
        description="Current TCP connections with the owning process where Windows makes it available. Presence is not a threat verdict."
        theme={theme}
        title="Active TCP connections"
      >
        {network ? (
          <div className="space-y-4 text-sm leading-6 text-slate-600">
            <p>
              Connections returned:{' '}
              <span className="font-medium text-slate-900">{network.tcp_connections.length}</span>
            </p>
            {network.tcp_connections.length ? (
              <ul className="max-h-96 space-y-3 overflow-y-auto border-t border-slate-800 pt-3">
                {network.tcp_connections.map((connection) => (
                  <li
                    key={`${connection.owning_process_id}-${connection.local_address}-${connection.local_port}-${connection.remote_address}-${connection.remote_port}`}
                  >
                    <p className="font-mono text-xs text-slate-900">
                      {connection.local_address}:{connection.local_port} →{' '}
                      {connection.remote_address}:{connection.remote_port}
                    </p>
                    <p className="text-xs text-slate-500">
                      {connection.owning_process_name || `PID ${connection.owning_process_id}`} ·{' '}
                      {connection.state}
                    </p>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : (
          <p className="text-sm text-slate-600">Reading Windows connections…</p>
        )}
      </DashboardPanel>
    </section>
  );

  const fileSecurityPage = (
    <section className="mt-7 grid gap-7 xl:grid-cols-[1.3fr_1fr]">
      <DashboardPanel
        description="This starts one Microsoft Defender custom scan only after you choose a specific existing folder and submit this form."
        theme={theme}
        title="Scan a selected folder"
      >
        <div className="space-y-4 text-sm leading-6 text-slate-600">
          {scanCapability ? (
            <SourceState
              available={
                scanCapability.state.status === 'available' && scanCapability.custom_scan_available
              }
              detail={scanCapability.state.detail}
              source="Microsoft Defender custom scan"
            />
          ) : (
            <p>Checking Defender custom-scan capability…</p>
          )}
          <form className="space-y-3" onSubmit={handleStartScan}>
            <label className="block font-medium text-slate-900" htmlFor="scan-directory">
              Absolute folder path
            </label>
            <input
              className="w-full rounded-2xl border border-slate-700 bg-slate-950/95 px-3 py-2 text-white outline-none transition focus:border-fuchsia-400 focus:ring-2 focus:ring-fuchsia-100"
              disabled={!scanCapability?.custom_scan_available || isStartingScan}
              id="scan-directory"
              onChange={(event) => setScanDirectory(event.target.value)}
              placeholder={'C:\\Users\\YourName\\Downloads\\Folder'}
              required
              value={scanDirectory}
            />
            <p className="text-xs text-slate-500">
              Drive roots, Windows folders, Program Files, and your entire user profile are blocked.
            </p>
            <button
              className="rounded-xl bg-gradient-to-r from-cyan-300 via-sky-400 to-violet-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow-[0_12px_30px_-12px_rgba(34,211,238,0.7)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
              disabled={!scanCapability?.custom_scan_available || isStartingScan}
              type="submit"
            >
              {isStartingScan ? 'Requesting Defender scan…' : 'Start Defender custom scan'}
            </button>
          </form>
          {scanAction ? (
            <div
              className={
                scanAction.state === 'started'
                  ? 'rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-3 text-emerald-100'
                  : 'rounded-xl border border-amber-400/20 bg-amber-400/5 p-3 text-amber-100'
              }
            >
              <p className="font-medium">{scanAction.detail}</p>
              <p className="mt-1 text-xs opacity-80">
                Requested {new Date(scanAction.requested_at).toLocaleString()}. Defender runs custom
                scans in the background and does not expose reliable per-folder progress or
                completion status to this interface.
              </p>
              <a
                className="mt-2 inline-block text-sm underline underline-offset-4"
                href="#security"
              >
                Review live Defender evidence
              </a>
            </div>
          ) : null}
          {scanError ? <p className="text-amber-700">{scanError}</p> : null}
        </div>
      </DashboardPanel>
      <DashboardPanel
        description="Scan findings remain Microsoft Defender evidence and appear in Security Center after Defender records them."
        theme={theme}
        title="Safety boundary"
      >
        <div className="space-y-3 text-sm leading-6 text-slate-600">
          <p>
            HATSS does not read file contents, delete files, move files, or quarantine anything.
          </p>
          <p>
            It only requests a Defender scan that you explicitly start. If Defender records a
            finding, it appears in Security Center with its source-reported remediation status.
          </p>
        </div>
      </DashboardPanel>
    </section>
  );

  const copilotPage = (
    <section className="mt-7 grid gap-7 xl:grid-cols-[1.3fr_1fr]">
      <DashboardPanel
        description="Ask general security questions or ask what the current HATSS evidence says about this device. It cannot run commands, change Defender, scan files, or act on the host."
        theme={theme}
        title="Evidence briefing"
      >
        <div className="space-y-4 text-sm leading-6 text-slate-600">
          {copilotStatus ? (
            <p className={copilotStatus.enabled ? 'text-emerald-700' : 'text-amber-700'}>
              {copilotStatus.detail} Model: {copilotStatus.model}.
            </p>
          ) : (
            <p>Checking local AI availability…</p>
          )}
          <form className="space-y-3" onSubmit={handleCopilotBrief}>
            <label className="block font-medium text-slate-900" htmlFor="copilot-question">
              Ask about device security or current evidence
            </label>
            <textarea
              className="min-h-28 w-full rounded-2xl border border-slate-700 bg-slate-950/95 px-3 py-2 text-white outline-none transition focus:border-fuchsia-400 focus:ring-2 focus:ring-fuchsia-100"
              disabled={!copilotStatus?.enabled || isRequestingBrief}
              id="copilot-question"
              minLength={3}
              onChange={(event) => setCopilotQuestion(event.target.value)}
              required
              value={copilotQuestion}
            />
            <p className="text-xs text-slate-500">
              Submitting explicitly shares a bounded local evidence summary—including system,
              Defender, Sysmon, and network telemetry—with the local Ollama model.
              Sysmon context can include command lines and file paths from recent events.
            </p>
            <button
              className="rounded-xl bg-gradient-to-r from-cyan-300 via-sky-400 to-violet-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow-[0_12px_30px_-12px_rgba(34,211,238,0.7)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
              disabled={!copilotStatus?.enabled || isRequestingBrief}
              type="submit"
            >
              {isRequestingBrief ? 'Generating local briefing…' : 'Request evidence briefing'}
            </button>
          </form>
          {copilotError ? <p className="text-amber-700">{copilotError}</p> : null}
          {copilotBrief ? (
            <div className="rounded-2xl border border-violet-200 bg-gradient-to-br from-violet-50 to-cyan-50 p-4 whitespace-pre-wrap text-slate-800">
              {copilotBrief.answer}
            </div>
          ) : null}
        </div>
      </DashboardPanel>
      <DashboardPanel
        description="No cloud model or API key is configured by HATSS."
        theme={theme}
        title="Enable local AI"
      >
        <div className="space-y-3 text-sm leading-6 text-slate-600">
          <p>
            Install Ollama and pull a model locally, then set{' '}
            <code className="text-fuchsia-600">HATSS_COPILOT_ENABLED=true</code> before starting the
            backend.
          </p>
          <p>
            Until then, this page remains deliberately disabled rather than pretending to be AI.
          </p>
        </div>
      </DashboardPanel>
    </section>
  );

  const facePage = (
    <section className="mt-7 grid gap-7">
      <FaceMonitor theme={theme} />
      <IntrusionGallery theme={theme} />
    </section>
  );

  const sensorsPage = (
    <section className="mt-7 grid gap-7">
      <SensorMonitor theme={theme} />
    </section>
  );

  const page =
    route === '#overview'
      ? overviewPage
      : route === '#security'
        ? securityPage
        : route === '#processes'
          ? processesPage
          : route === '#network'
            ? networkPage
            : route === '#files'
              ? fileSecurityPage
              : route === '#face'
                ? facePage
                : route === '#sensors'
                  ? sensorsPage
                  : copilotPage;

  return (
    <div className={`app-shell min-h-screen bg-transparent ${theme === 'dark' ? 'text-slate-100' : 'text-slate-800'}`}>
      <a
        className="absolute left-4 top-[-5rem] z-50 rounded-md bg-gradient-to-r from-fuchsia-500 to-cyan-500 px-4 py-2 font-semibold text-white transition focus:top-4"
        href="#main-content"
      >
        Skip to dashboard
      </a>
      <div className="lg:flex">
        <Sidebar activeRoute={route} theme={theme} />
        <main className="min-w-0 flex-1 px-5 py-7 sm:px-8 lg:px-10 lg:py-9" id="main-content">
          <header className={`flex flex-col justify-between gap-5 rounded-3xl border px-5 py-5 shadow-[0_20px_60px_-24px_rgba(15,23,42,0.25)] backdrop-blur sm:flex-row sm:items-center sm:px-6 ${theme === 'dark' ? 'border-slate-700/80 bg-slate-900/80' : 'border-slate-200/80 bg-white/80'}`}>
            <div>
              <p className="text-sm font-medium text-fuchsia-600">HATSS · local host monitoring</p>
              <h1 className={`mt-1 text-3xl font-semibold tracking-tight ${theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}`}>{title}</h1>
              <p className={`mt-2 text-sm ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>{description}</p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button
                aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
                className={`rounded-2xl border px-3 py-2 text-sm font-medium transition hover:-translate-y-0.5 ${theme === 'dark' ? 'border-slate-700 bg-slate-800 text-slate-100 hover:bg-slate-700' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                type="button"
              >
                {theme === 'dark' ? '☀️ Light mode' : '🌙 Dark mode'}
              </button>
              <div className={`flex items-center gap-3 rounded-2xl border px-3 py-2.5 text-sm shadow-sm ${theme === 'dark' ? 'border-emerald-400/20 bg-emerald-500/10 text-emerald-300' : 'border-emerald-200 bg-emerald-50 text-emerald-700'}`}>
                <span aria-hidden="true" className="size-2 rounded-full bg-emerald-500 shadow-[0_0_10px_#86efac]" />
                {overview
                  ? `Live · ${new Date(overview.observed_at).toLocaleTimeString()}`
                  : 'Connecting to local API'}
              </div>
            </div>
          </header>
          {error && (
            <div
              className={`mt-6 rounded-xl border px-4 py-3 text-sm ${theme === 'dark' ? 'border-amber-400/30 bg-amber-400/10 text-amber-100' : 'border-amber-400/30 bg-amber-400/10 text-amber-800'}`}
              role="alert"
            >
              {error}
            </div>
          )}
          {loading && !overview ? (
            <p className={`mt-8 text-sm ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>Reading host telemetry…</p>
          ) : null}
          {route === '#security' ||
          route === '#network' ||
          route === '#files' ||
          route === '#face' ||
          route === '#sensors' ||
          route === '#copilot'
            ? page
            : overview
              ? page
              : null}
        </main>
      </div>
    </div>
  );
}
