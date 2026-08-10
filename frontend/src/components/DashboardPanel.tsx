import type { ReactNode } from 'react';

interface DashboardPanelProps {
  children: ReactNode;
  description?: string;
  title: string;
  theme?: 'light' | 'dark';
}

export function DashboardPanel({ children, description, title, theme = 'light' }: DashboardPanelProps) {
  return (
    <section className={`rounded-3xl border p-5 shadow-[0_20px_60px_-26px_rgba(15,23,42,0.25)] backdrop-blur-xl transition duration-200 hover:-translate-y-1 hover:shadow-[0_24px_70px_-22px_rgba(244,114,182,0.35)] sm:p-6 ${theme === 'dark' ? 'border-slate-700/80 bg-slate-900/80' : 'border-slate-200/80 bg-white/85'}`}>
      <div className="mb-5">
        <h2 className={`text-base font-semibold ${theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}`}>{title}</h2>
        {description ? <p className={`mt-1 text-sm ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>{description}</p> : null}
      </div>
      {children}
    </section>
  );
}
