interface HealthItem {
  label: string;
  status: string;
  value: string;
  valuePercent: number;
}

interface SystemHealthProps {
  items: readonly HealthItem[];
  theme?: 'light' | 'dark';
}

export function SystemHealth({ items, theme = 'light' }: SystemHealthProps) {
  return (
    <ul className="space-y-5">
      {items.map((item) => (
        <li key={item.label}>
          <div className="flex items-center justify-between gap-4 text-sm">
            <span className={`font-medium ${theme === 'dark' ? 'text-slate-100' : 'text-slate-800'}`}>{item.label}</span>
            <span className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
              {item.value} <span className={theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}>·</span> {item.status}
            </span>
          </div>
          <div aria-hidden="true" className={`mt-2 h-2.5 overflow-hidden rounded-full ${theme === 'dark' ? 'bg-slate-700' : 'bg-slate-200'}`}>
            <div
              className="h-full rounded-full bg-gradient-to-r from-fuchsia-500 via-violet-500 to-cyan-500 transition-[width] duration-500"
              style={{ width: `${Math.min(Math.max(item.valuePercent, 0), 100)}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}
