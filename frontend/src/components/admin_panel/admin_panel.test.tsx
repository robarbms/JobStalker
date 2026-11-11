import React from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import AdminPanel, { ScraperSettings, ScraperStatus } from './admin_panel';

const initialSettings: ScraperSettings = {
    keywords: ['engineer'], max_jobs: 100, companies: ['Reddit', 'Zillow'],
    schedule: { enabled: false, interval_minutes: 120, times: [], weekdays: [0, 1, 2, 3, 4, 5, 6], timezone: 'UTC' },
};
const online: ScraperStatus = {
    worker_online: true, worker_started_at: '2026-11-09T08:00:00Z',
    next_run_at: null, active_run: null, last_run: null,
};
const companies = [
    { name: 'Bose', location: 'Boston' }, { name: 'Reddit', location: 'Remote' },
    { name: 'Zillow', location: 'Seattle' },
];
const queued: ScraperStatus = {
    ...online, active_run: {
        id: 1, source: 'manual', status: 'queued', requested_at: '2026-11-09T09:00:00Z',
        started_at: null, finished_at: null, jobs_found: 0, jobs_added: 0, errors: [],
    },
};

function reply(data: unknown, ok = true): Response {
    return { ok, status: ok ? 200 : 400, json: async () => data } as Response;
}

const originalFetch = global.fetch;
let fetchMock: jest.MockedFunction<typeof fetch>;
let settings: ScraperSettings;
let status: ScraperStatus;

beforeEach(() => {
    settings = JSON.parse(JSON.stringify(initialSettings));
    status = { ...online };
    fetchMock = jest.fn(async (url, options) => {
        if (String(url).endsWith('/status')) return reply(status);
        if (String(url).endsWith('/run')) {
            status = queued;
            return reply({ run_id: 1, status });
        }
        if (options?.method === 'PUT') settings = JSON.parse(String(options.body));
        return reply({ settings, companies, status });
    });
    global.fetch = fetchMock;
});

afterEach(() => {
    jest.useRealTimers();
    global.fetch = originalFetch;
});

test('does not fetch while closed and loads saved controls when opened', async () => {
    const { rerender } = render(<AdminPanel open={false} setAdminPanel={jest.fn()} />);
    expect(fetchMock).not.toHaveBeenCalled();
    rerender(<AdminPanel open setAdminPanel={jest.fn()} />);
    expect(await screen.findByLabelText('Keywords')).toHaveValue('engineer');
    expect(screen.getByRole('button', { name: 'Save changes' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Scrape now' })).toBeEnabled();
    expect(screen.getByRole('checkbox', { name: /Bose/ })).not.toBeChecked();
});

test('saves keywords, per-company limit, companies and combined schedules to the backend', async () => {
    render(<AdminPanel open setAdminPanel={jest.fn()} />);
    fireEvent.change(await screen.findByLabelText('Keywords'), { target: { value: 'rust\nplatform' } });
    fireEvent.change(screen.getByLabelText(/^Max new jobs/), { target: { value: '3' } });
    fireEvent.click(screen.getByRole('checkbox', { name: /Bose/ }));
    fireEvent.click(screen.getByRole('checkbox', { name: /Zillow/ }));
    fireEvent.click(screen.getByLabelText('Enable schedule'));
    fireEvent.change(screen.getByLabelText('Interval in minutes'), { target: { value: '5' } });
    fireEvent.change(screen.getByLabelText(/Specific times/), { target: { value: '09:00, 17:30' } });
    fireEvent.click(screen.getByRole('checkbox', { name: 'Sunday' }));
    fireEvent.change(screen.getByLabelText('Schedule timezone'), { target: { value: 'America/New_York' } });
    expect(screen.getByRole('button', { name: 'Scrape now' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));
    expect(await screen.findByText('Scraper settings saved.')).toBeInTheDocument();
    const call = fetchMock.mock.calls.find(([, options]) => options?.method === 'PUT');
    expect(JSON.parse(String(call?.[1]?.body))).toEqual({
        keywords: ['rust', 'platform'], max_jobs: 3, companies: ['Bose', 'Reddit'],
        schedule: { enabled: true, interval_minutes: 5, times: ['09:00', '17:30'],
            weekdays: [0, 1, 2, 3, 4, 5], timezone: 'America/New_York' },
    });
    expect(screen.getByRole('button', { name: 'Scrape now' })).toBeEnabled();
});

test('queues a manual scrape and polls until it completes without allowing duplicates', async () => {
    jest.useFakeTimers();
    render(<AdminPanel open setAdminPanel={jest.fn()} />);
    await screen.findByLabelText('Keywords');
    fireEvent.click(screen.getByRole('button', { name: 'Scrape now' }));
    expect(await screen.findByText('Scrape queued')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Scrape now' })).toBeDisabled();
    status = {
        ...online, last_run: {
            ...queued.active_run!, status: 'completed', jobs_found: 8, jobs_added: 3,
            finished_at: '2026-11-09T09:02:00Z',
        },
    };
    await act(async () => { jest.advanceTimersByTime(5000); });
    expect(screen.getByText('Ready to scrape')).toBeInTheDocument();
    expect(screen.getByText(/3 added \/ 8 found/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Scrape now' })).toBeEnabled();
    expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/run'))).toHaveLength(1);
});

test('keeps unsaved controls and displays API validation failures', async () => {
    render(<AdminPanel open setAdminPanel={jest.fn()} />);
    fireEvent.change(await screen.findByLabelText('Keywords'), { target: { value: 'rust' } });
    fetchMock.mockResolvedValueOnce(reply({ error: 'Select at least one weekday.' }, false));
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Select at least one weekday.');
    expect(screen.getByLabelText('Keywords')).toHaveValue('rust');
    expect(screen.getByRole('button', { name: 'Scrape now' })).toBeDisabled();
});

test('offers retry on load failure and disables manual controls when the worker is offline', async () => {
    fetchMock.mockRejectedValueOnce(new Error('Network unavailable'));
    render(<AdminPanel open setAdminPanel={jest.fn()} />);
    expect(await screen.findByRole('alert')).toHaveTextContent('Network unavailable');
    status = { ...online, worker_online: false };
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
    expect(await screen.findByText('Worker offline')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Scrape now' })).toBeDisabled();
});

test('supports days-only schedules and rejects an empty company selection before saving', async () => {
    render(<AdminPanel open setAdminPanel={jest.fn()} />);
    await screen.findByLabelText('Keywords');
    fireEvent.click(screen.getByLabelText('Repeat at a timed interval'));
    fireEvent.click(screen.getByLabelText('Enable schedule'));
    fireEvent.click(screen.getByRole('button', { name: 'Clear all' }));
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('select at least one company');
    expect(fetchMock.mock.calls.some(([, options]) => options?.method === 'PUT')).toBe(false);
    fireEvent.click(screen.getByRole('checkbox', { name: /Reddit/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));
    await screen.findByText('Scraper settings saved.');
    expect(settings.schedule.interval_minutes).toBeNull();
    expect(settings.schedule.times).toEqual([]);
});

test('shows run failures, filters companies, and closes with Escape', async () => {
    status = {
        ...online, last_run: {
            ...queued.active_run!, status: 'failed', errors: ['Reddit: connection failed'],
            finished_at: '2026-11-09T09:02:00Z',
        },
    };
    const close = jest.fn();
    render(<AdminPanel open setAdminPanel={close} />);
    await screen.findByLabelText('Keywords');
    expect(screen.getByText('Reddit: connection failed')).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Find a company'), { target: { value: 'reddit' } });
    expect(screen.queryByRole('checkbox', { name: /Bose/ })).not.toBeInTheDocument();
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' });
    await waitFor(() => expect(close).toHaveBeenCalledWith(false));
});
