import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { App } from '../App';

describe('App', () => {
  afterEach(() => vi.restoreAllMocks());

  it('renders live telemetry without inventing a security score', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((input: string) => {
        const body = input.endsWith('/system/overview')
          ? {
              cpu: { logical_cores: 8, physical_cores: 4, usage_percent: 24.5 },
              data_mode: 'live',
              disk: { free_bytes: 1000, total_bytes: 2000, usage_percent: 50, used_bytes: 1000 },
              host: {
                booted_at: '2026-01-01T00:00:00Z',
                hostname: 'test-host',
                operating_system: 'Windows',
                uptime_seconds: 3600,
              },
              memory: {
                available_bytes: 1000,
                total_bytes: 2000,
                usage_percent: 50,
                used_bytes: 1000,
              },
              observed_at: '2026-01-01T00:00:00Z',
              process_collection_status: 'available',
              running_processes: 3,
              source: 'native',
              top_processes: [],
            }
          : input.endsWith('/security/defender')
            ? {
                antivirus_enabled: true,
                behavior_monitor_enabled: true,
                detections: [],
                engine_version: 'test',
                real_time_protection_enabled: true,
                signature_last_updated: null,
                source: 'microsoft_defender',
                state: {
                  detail: 'Reported directly by Microsoft Defender.',
                  observed_at: '2026-01-01T00:00:00Z',
                  status: 'available',
                },
              }
            : {
                events: [],
                source: 'sysmon',
                state: {
                  detail: 'Recent events read directly from the Sysmon operational log.',
                  observed_at: '2026-01-01T00:00:00Z',
                  status: 'available',
                },
              };
        return Promise.resolve({ json: async () => body, ok: true });
      }),
    );
    render(<App />);

    expect(screen.getByRole('heading', { name: 'Live system overview' })).toBeInTheDocument();
    expect(await screen.findByText('test-host')).toBeVisible();
    expect(screen.getByText('Defender summary')).toBeVisible();
  });

  it('uses separate hash-routed pages for security evidence', async () => {
    window.location.hash = '#security';
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        json: async () => ({
          events: [],
          state: {
            detail: 'Source unavailable for this test.',
            observed_at: '2026-01-01T00:00:00Z',
            status: 'unavailable',
          },
        }),
        ok: true,
      }),
    );
    render(<App />);

    expect(screen.getByRole('heading', { name: 'Security center' })).toBeInTheDocument();
    expect(await screen.findByText('Microsoft Defender evidence')).toBeVisible();
    expect(screen.getByText('Sysmon evidence')).toBeVisible();
    fireEvent.click(screen.getByRole('link', { name: 'Network' }));
    expect(await screen.findByRole('heading', { name: 'Network' })).toBeVisible();
    expect(screen.getByText('Network monitoring')).toBeVisible();
  });

  it('toggles between light and dark themes', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ json: async () => ({}), ok: true }));
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /switch to dark mode/i }));
    expect(document.documentElement.dataset.theme).toBe('dark');

    fireEvent.click(screen.getByRole('button', { name: /switch to light mode/i }));
    expect(document.documentElement.dataset.theme).toBe('light');
  });
});
