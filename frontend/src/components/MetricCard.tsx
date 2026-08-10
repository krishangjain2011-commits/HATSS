interface MetricCardProps {
  change: string;
  label: string;
  tone: 'blue' | 'emerald' | 'amber' | 'violet';
  value: string;
  theme?: 'light' | 'dark';
}

const toneClasses = {
  amber: 'bg-amber-100 text-amber-700 ring-amber-200',
  blue: 'bg-sky-100 text-sky-700 ring-sky-200',
  emerald: 'bg-emerald-100 text-emerald-700 ring-emerald-200',
  violet: 'bg-violet-100 text-violet-700 ring-violet-200',
} as const;

export function MetricCard({ change, label, tone, value, theme = 'light' }: MetricCardProps) {
  return (
    <article className={`group rounded-3xl border p-5 shadow-[0_18px_45px_-22px_rgba(15,23,42,0.35)] transition duration-200 hover:-translate-y-1 hover:shadow-[0_22px_55px_-20px_rgba(244,114,182,0.4)] ${theme === 'dark' ? 'border-slate-700/80 bg-gradient-to-br from-slate-900 via-slate-800 to-violet-950/70' : 'border-slate-200/80 bg-gradient-to-br from-white via-slate-50 to-violet-50/70'}`}>
      <div className="flex items-center justify-between gap-3">
        <p className={`text-sm font-medium ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>{label}</p>
        <span
          className={[
            'grid size-9 place-items-center rounded-xl text-xs font-bold ring-1',
            toneClasses[tone],
          ].join(' ')}
        >
          {label.slice(0, 1)}
        </span>
      </div>
      <p className={`mt-5 text-3xl font-semibold tracking-tight ${theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}`}>{value}</p>
      <p className={`mt-2 text-xs ${theme === 'dark' ? 'text-slate-500' : 'text-slate-500'}`}>{change}</p>
    </article>
  );
}
