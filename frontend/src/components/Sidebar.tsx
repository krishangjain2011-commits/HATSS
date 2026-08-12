const navigationItems = [
  { href: '#overview', label: 'Overview', mark: 'O' },
  { href: '#security', label: 'Security center', mark: 'S' },
  { href: '#processes', label: 'Processes', mark: 'P' },
  { href: '#network', label: 'Network', mark: 'N' },
  { href: '#files', label: 'File security', mark: 'F' },
  { href: '#face', label: 'Face recognition', mark: 'R' },
  { href: '#sensors', label: 'Sensors', mark: 'E' },
] as const;

interface SidebarProps {
  activeRoute: string;
  theme?: 'light' | 'dark';
}

export function Sidebar({ activeRoute, theme = 'light' }: SidebarProps) {
  return (
    <aside className={`border-b backdrop-blur-xl lg:sticky lg:top-0 lg:h-screen lg:w-64 lg:shrink-0 lg:border-r lg:border-b-0 ${theme === 'dark' ? 'border-slate-700/80 bg-slate-950/80' : 'border-slate-200/80 bg-white/85'}`}>
      <div className="flex h-full flex-col px-4 py-5">
        <div className={`flex items-center gap-3 rounded-2xl border px-3 py-3 shadow-sm ${theme === 'dark' ? 'border-violet-700/40 bg-gradient-to-r from-violet-950/70 to-cyan-950/70' : 'border-violet-200 bg-gradient-to-r from-violet-50 to-cyan-50'}`}>
          <span
            aria-hidden="true"
            className="grid size-10 place-items-center rounded-xl bg-gradient-to-br from-fuchsia-500 via-violet-500 to-cyan-500 text-base font-black text-white shadow-lg shadow-violet-300/60"
          >
            H
          </span>
          <div>
            <p className={`font-semibold tracking-wide ${theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}`}>HATSS</p>
            <p className={`text-xs ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Security workspace</p>
          </div>
        </div>

        <nav aria-label="Primary" className="mt-8 overflow-x-auto lg:overflow-visible">
          <ul className="flex min-w-max gap-2 lg:flex-col">
            {navigationItems.map((item) => {
              const isCurrent = item.href === activeRoute;

              return (
                <li key={item.href}>
                  <a
                    aria-current={isCurrent ? 'page' : undefined}
                    className={
                      isCurrent
                        ? `flex items-center gap-3 rounded-2xl bg-gradient-to-r from-violet-500/15 to-cyan-500/15 px-3 py-2.5 text-sm font-medium ring-1 ring-violet-200 transition hover:-translate-y-0.5 ${theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}`
                        : `flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm transition hover:-translate-y-0.5 ${theme === 'dark' ? 'text-slate-400 hover:bg-slate-800 hover:text-slate-100 focus-visible:bg-slate-800 focus-visible:text-slate-100' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 focus-visible:bg-slate-100 focus-visible:text-slate-900'}`
                    }
                    href={item.href}
                  >
                    <span
                      aria-hidden="true"
                      className={
                        isCurrent
                          ? 'grid size-6 place-items-center rounded-md bg-gradient-to-br from-fuchsia-500 to-cyan-500 text-[10px] font-bold text-white'
                          : `grid size-6 place-items-center rounded-md text-[10px] font-bold ${theme === 'dark' ? 'bg-slate-800 text-slate-300' : 'bg-slate-100 text-slate-600'}`
                      }
                    >
                      {item.mark}
                    </span>
                    {item.label}
                  </a>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className={`mt-8 hidden rounded-2xl border p-4 lg:block ${theme === 'dark' ? 'border-violet-700/40 bg-gradient-to-br from-violet-950/70 to-cyan-950/70' : 'border-violet-200 bg-gradient-to-br from-violet-50 to-cyan-50'}`}>
          <p className="text-xs font-semibold tracking-[0.12em] text-fuchsia-600 uppercase">
            Live telemetry
          </p>
          <p className={`mt-2 text-sm leading-6 ${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>
            Local CPU, memory, disk, Defender, and available Sysmon evidence are read directly from
            the HATSS API.
          </p>
        </div>

        <div className={`mt-auto hidden items-center gap-3 rounded-2xl border px-3 py-3 lg:flex ${theme === 'dark' ? 'border-slate-700 bg-slate-800/90' : 'border-slate-200 bg-slate-50'}`}>
          <span className="grid size-9 place-items-center rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 text-xs font-semibold text-white">
            HV
          </span>
          <div>
            <p className={`text-sm font-medium ${theme === 'dark' ? 'text-slate-100' : 'text-slate-800'}`}>Local workspace</p>
            <p className={`text-xs ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Read-only monitoring</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
