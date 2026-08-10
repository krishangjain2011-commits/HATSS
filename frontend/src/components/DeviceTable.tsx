export interface Device {
  activity: string;
  name: string;
  status: string;
  type: string;
}

interface DeviceTableProps {
  devices: readonly Device[];
  theme?: 'light' | 'dark';
}

export function DeviceTable({ devices, theme = 'light' }: DeviceTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[520px] text-left text-sm">
        <thead className={`border-b text-xs tracking-[0.14em] uppercase ${theme === 'dark' ? 'border-slate-700 text-slate-400' : 'border-slate-200 text-slate-500'}`}>
          <tr>
            <th className="pb-3 font-medium">Process</th>
            <th className="pb-3 font-medium">Identifier</th>
            <th className="pb-3 font-medium">Memory share</th>
            <th className="pb-3 text-right font-medium">Status</th>
          </tr>
        </thead>
        <tbody className={`divide-y ${theme === 'dark' ? 'divide-slate-700' : 'divide-slate-200'}`}>
          {devices.map((device) => {
            return (
              <tr className={`transition ${theme === 'dark' ? 'text-slate-300 hover:bg-slate-800/70' : 'text-slate-700 hover:bg-violet-50/70'}`} key={device.name}>
                <td className={`py-4 font-medium ${theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}`}>{device.name}</td>
                <td className={`py-4 ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>{device.type}</td>
                <td className={`py-4 ${theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}`}>{device.activity}</td>
                <td className="py-4 text-right">
                  <span className="rounded-full bg-gradient-to-r from-violet-500 to-cyan-500 px-2.5 py-1 font-mono text-xs font-medium text-white ring-1 ring-white/70">
                    {device.status}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
