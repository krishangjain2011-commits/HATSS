import { useEffect, useState } from 'react';

interface IntrusionGalleryProps {
  theme: 'light' | 'dark';
}

export function IntrusionGallery({ theme }: IntrusionGalleryProps) {
  const [intrusions, setIntrusions] = useState<string[]>([]);
  const [metrics, setMetrics] = useState({ total_events: 0, recent_events: 0 });

  useEffect(() => {
    const fetchIntrusions = async () => {
      try {
        const [metricsRes, listRes] = await Promise.all([
          fetch('/api/v1/intrusions/metrics'),
          fetch('/api/v1/intrusions/list?limit=6'),
        ]);

        const metricsData = await metricsRes.json();
        const listData = await listRes.json();

        setMetrics(metricsData);
        setIntrusions(listData);
      } catch (error) {
        console.error('Intrusion data error:', error);
      }
    };

    fetchIntrusions();
    const interval = setInterval(fetchIntrusions, 3000);
    return () => clearInterval(interval);
  }, []);

  const bgColor = theme === 'dark' ? 'bg-slate-950' : 'bg-white';
  const textColor = theme === 'dark' ? 'text-white' : 'text-slate-900';
  const borderColor = theme === 'dark' ? 'border-slate-700' : 'border-slate-300';

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className={`${bgColor} rounded-xl border ${borderColor} p-4`}>
          <p className="text-xs font-medium text-slate-500 uppercase">Total Events</p>
          <p className={`text-2xl font-bold mt-2 ${textColor}`}>{metrics.total_events}</p>
        </div>

        <div className={`${bgColor} rounded-xl border ${borderColor} p-4`}>
          <p className="text-xs font-medium text-slate-500 uppercase">Recent Images</p>
          <p className={`text-2xl font-bold mt-2 ${textColor}`}>{metrics.recent_events}</p>
        </div>
      </div>

      <div className={`${bgColor} rounded-xl border ${borderColor} p-4`}>
        <p className="text-xs font-medium text-slate-500 uppercase mb-3">Latest Alerts</p>

        {intrusions.length === 0 ? (
          <p className="text-sm text-emerald-600 font-medium">✅ No intrusions detected</p>
        ) : (
          <div className="grid grid-cols-2 gap-2 md:grid-cols-3 overflow-y-auto max-h-64">
            {intrusions.map((image) => (
              <a
                key={image}
                href={`/intruder_snaps/${image}`}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg overflow-hidden border border-red-500/30 hover:border-red-500 hover:shadow-lg transition"
              >
                <img
                  src={`/intruder_snaps/${image}`}
                  alt="Intrusion"
                  className="w-full h-24 object-cover"
                />
                <div className="bg-red-500/10 p-1 text-center">
                  <p className="text-xs text-red-500 font-mono">{image}</p>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
