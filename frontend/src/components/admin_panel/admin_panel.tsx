import React, { useEffect, useRef, useState } from 'react';
import { requestJson } from '../../utils/api';
import './admin_panel.css';

export type AdminPanelProps = {
    open: boolean;
    setAdminPanel: (isOpen: boolean) => void;
};

export type ScraperSettings = {
    keywords: string[];
    max_jobs: number;
    companies: string[];
    schedule: {
        enabled: boolean;
        interval_minutes: number | null;
        times: string[];
        weekdays: number[];
        timezone: string;
    };
};

type ScrapeRun = {
    id: number;
    source: string;
    status: string;
    requested_at: string;
    started_at: string | null;
    finished_at: string | null;
    jobs_found: number;
    jobs_added: number;
    errors: string[];
};

export type ScraperStatus = {
    worker_online: boolean;
    worker_started_at: string | null;
    next_run_at: string | null;
    active_run: ScrapeRun | null;
    last_run: ScrapeRun | null;
};

type AdminData = {
    settings: ScraperSettings;
    companies: { name: string; location: string }[];
    status: ScraperStatus;
};

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const splitKeywords = (text: string) => Array.from(new Set(
    text.split(/[,\n]+/).map(word => word.trim().toLowerCase()).filter(Boolean),
));
const message = (error: unknown) => error instanceof Error ? error.message : 'The request could not be completed.';
const displayTime = (time: string | null) => time
    ? new Date(time).toLocaleString(undefined, { timeZoneName: 'short' }) : 'Not scheduled';

const AdminPanel = ({ open, setAdminPanel }: AdminPanelProps) => {
    const [settings, setSettings] = useState<ScraperSettings | null>(null);
    const [saved, setSaved] = useState<ScraperSettings | null>(null);
    const [companies, setCompanies] = useState<AdminData['companies']>([]);
    const [status, setStatus] = useState<ScraperStatus | null>(null);
    const [keywords, setKeywords] = useState('');
    const [maxJobs, setMaxJobs] = useState('100');
    const [useInterval, setUseInterval] = useState(true);
    const [interval, setIntervalValue] = useState('120');
    const [times, setTimes] = useState('');
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [starting, setStarting] = useState(false);
    const [error, setError] = useState('');
    const [statusError, setStatusError] = useState('');
    const [notice, setNotice] = useState('');
    const [reload, setReload] = useState(0);
    const panel = useRef<HTMLElement>(null);

    function loadSettings(data: AdminData) {
        setSettings(data.settings);
        setSaved(data.settings);
        setCompanies(data.companies);
        setStatus(data.status);
        setKeywords(data.settings.keywords.join('\n'));
        setMaxJobs(String(data.settings.max_jobs));
        setUseInterval(data.settings.schedule.interval_minutes !== null);
        setIntervalValue(String(data.settings.schedule.interval_minutes ?? 120));
        setTimes(data.settings.schedule.times.join(', '));
    }

    useEffect(() => {
        if (!open) return;
        const controller = new AbortController();
        let closed = false;
        let timer: ReturnType<typeof setTimeout>;
        setSettings(null);
        setSaved(null);
        setStatus(null);
        setLoading(true);
        setError('');
        setStatusError('');
        setNotice('');

        async function poll() {
            try {
                const current = await requestJson<ScraperStatus>('/admin/scraper/status', { signal: controller.signal });
                if (!closed) {
                    setStatus(current);
                    setStatusError('');
                }
            } catch (error) {
                if (!closed) {
                    setStatusError(`Could not refresh scraper status: ${message(error)}`);
                    setStatus(previous => previous ? { ...previous, worker_online: false } : previous);
                }
            } finally {
                if (!closed) timer = setTimeout(poll, 5000);
            }
        }

        async function load() {
            try {
                const data = await requestJson<AdminData>('/admin/scraper', { signal: controller.signal });
                if (!closed) {
                    loadSettings(data);
                    timer = setTimeout(poll, 5000);
                }
            } catch (error) {
                if (!closed) setError(`Could not load scraper settings: ${message(error)}`);
            } finally {
                if (!closed) setLoading(false);
            }
        }
        load();
        return () => {
            closed = true;
            controller.abort();
            clearTimeout(timer);
        };
    }, [open, reload]);

    useEffect(() => {
        if (!open) return;
        const previous = document.activeElement;
        const overflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        panel.current?.focus();
        return () => {
            document.body.style.overflow = overflow;
            if (previous instanceof HTMLElement) previous.focus();
        };
    }, [open]);

    if (!open) return null;

    const payload: ScraperSettings | null = settings ? {
        ...settings, keywords: splitKeywords(keywords), max_jobs: Number(maxJobs),
        companies: [...settings.companies].sort((a, b) => a.localeCompare(b)),
        schedule: {
            ...settings.schedule, interval_minutes: useInterval ? Number(interval) : null,
            times: Array.from(new Set(times.split(/[,\s]+/).filter(Boolean))).sort(),
        },
    } : null;
    const dirty = Boolean(payload && saved && JSON.stringify(payload) !== JSON.stringify(saved));
    const active = status?.active_run;
    const last = status?.last_run;
    const canRun = status?.worker_online && !active && !dirty && !saving && !starting;
    const filteredCompanies = companies.filter(company => company.name.toLowerCase().includes(search.toLowerCase()));

    function updateSchedule(patch: Partial<ScraperSettings['schedule']>) {
        setSettings(previous => previous ? {
            ...previous, schedule: { ...previous.schedule, ...patch },
        } : previous);
    }

    function toggleCompany(name: string) {
        setSettings(previous => previous ? {
            ...previous, companies: previous.companies.includes(name)
                ? previous.companies.filter(company => company !== name) : [...previous.companies, name],
        } : previous);
    }

    async function save(event: React.FormEvent) {
        event.preventDefault();
        if (!payload) return;
        setError('');
        setNotice('');
        if (!payload.keywords.length || !payload.companies.length) {
            setError('Enter at least one keyword and select at least one company.');
            return;
        }
        setSaving(true);
        try {
            const data = await requestJson<AdminData>('/admin/scraper', {
                method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
            });
            loadSettings(data);
            setNotice('Scraper settings saved.');
        } catch (error) {
            setError(`Could not save scraper settings: ${message(error)}`);
        } finally {
            setSaving(false);
        }
    }

    async function scrapeNow() {
        setError('');
        setNotice('');
        setStarting(true);
        try {
            const result = await requestJson<{ status: ScraperStatus }>('/admin/scraper/run', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}',
            });
            setStatus(result.status);
            setNotice('Scrape queued using your saved settings.');
        } catch (error) {
            setError(`Could not start a scrape: ${message(error)}`);
        } finally {
            setStarting(false);
        }
    }

    function handleKey(event: React.KeyboardEvent) {
        if (event.key === 'Escape') setAdminPanel(false);
        if (event.key !== 'Tab') return;
        const elements = panel.current?.querySelectorAll<HTMLElement>(
            'button:not(:disabled), input:not(:disabled), textarea:not(:disabled), [tabindex="0"]',
        );
        if (!elements?.length) return;
        const first = elements[0];
        const last = elements[elements.length - 1];
        if (event.shiftKey && (document.activeElement === first || document.activeElement === panel.current)) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    return <>
        <button className="admin-backdrop" aria-hidden="true" tabIndex={-1} onClick={() => setAdminPanel(false)} />
        <aside className="admin-panel" role="dialog" aria-modal="true" aria-labelledby="admin-title"
            ref={panel} tabIndex={-1} onKeyDown={handleKey}>
            <header className="admin-panel-header">
                <div><h2 id="admin-title">Admin Panel</h2><p>Scraper controls</p></div>
                <button type="button" className="admin-panel-close" aria-label="Close Admin Panel"
                    onClick={() => setAdminPanel(false)}>x</button>
            </header>
            {loading ? <p role="status">Loading scraper settings...</p> : null}
            {error ? <p className="admin-error" role="alert">{error}</p> : null}
            {!loading && !settings ? <button onClick={() => setReload(value => value + 1)}>Retry</button> : null}
            {!loading && settings && payload ? <>
                <section className="admin-run" aria-label="Scraper status">
                    <div>
                        <h3>{!status?.worker_online ? 'Worker offline' : active
                            ? active.status === 'queued' ? 'Scrape queued' : 'Scrape running' : 'Ready to scrape'}</h3>
                        <p>{!status?.worker_online
                            ? 'Start backend\\main.py to enable manual and scheduled scrapes.'
                            : active ? `${active.jobs_added} added / ${active.jobs_found} found so far. Only one scrape runs at a time.`
                                : `Next scheduled scrape (local time): ${displayTime(status.next_run_at)}`}</p>
                    </div>
                    <button type="button" className="admin-primary" disabled={!canRun} onClick={scrapeNow}>
                        {starting ? 'Queuing...' : 'Scrape now'}
                    </button>
                    {dirty ? <p className="admin-run-hint">Save changes before starting a manual scrape.</p> : null}
                    {last ? <p className="admin-run-hint">Last run: {last.status.replace(/_/g, ' ')}.
                        {' '}{last.jobs_added} added / {last.jobs_found} found.
                        {' '}{displayTime(last.finished_at)}</p> : null}
                    {(active || last)?.errors.length ? <details className="admin-run-hint admin-error">
                        <summary>Scrape issues ({(active || last)?.errors.length})</summary>
                        <ul>{(active || last)?.errors.map((error, index) => <li key={index}>{error}</li>)}</ul>
                    </details> : null}
                    {statusError ? <p className="admin-error" role="alert">{statusError}</p> : null}
                </section>
                <form onSubmit={save}>
                    <fieldset className="admin-fields" disabled={saving}>
                        <section className="admin-section admin-query-grid" aria-label="Search settings">
                            <label><span className="admin-field-title">Keywords</span>
                                <textarea aria-label="Keywords" value={keywords} rows={5} required
                                    onChange={event => setKeywords(event.target.value)} />
                                <span className="admin-help">One per line or separated by commas. Titles must match at least one.</span>
                            </label>
                            <label>Max new jobs per company
                                <input type="number" min="1" step="1" required value={maxJobs}
                                    onChange={event => setMaxJobs(event.target.value)} />
                                <span className="admin-help">Per run, across all keywords. Known jobs do not use this limit.</span>
                            </label>
                        </section>
                        <section className="admin-section" aria-labelledby="admin-schedule-title">
                            <div className="admin-section-heading">
                                <h3 id="admin-schedule-title">Schedule</h3>
                                <label className="admin-check"><input type="checkbox" checked={settings.schedule.enabled}
                                    onChange={event => updateSchedule({ enabled: event.target.checked })} /> Enable schedule</label>
                            </div>
                            <label className="admin-check"><input type="checkbox" checked={useInterval}
                                onChange={event => setUseInterval(event.target.checked)} /> Repeat at a timed interval</label>
                            <div className="admin-two-columns">
                                <label>Interval in minutes
                                    <input type="number" min="1" step="1" required={useInterval} disabled={!useInterval}
                                        value={interval} onChange={event => setIntervalValue(event.target.value)} />
                                </label>
                                <label>Specific times
                                    <input type="text" placeholder="09:00, 17:30" value={times}
                                        onChange={event => setTimes(event.target.value)} />
                                    <span className="admin-help">24-hour times, separated by commas.</span>
                                </label>
                            </div>
                            <p className="admin-help">Intervals wait at least 30 minutes after worker startup.
                                Later runs wait the configured interval after the previous run finishes.
                                Specific times and manual scrapes do not use the startup delay.</p>
                            <fieldset className="admin-days"><legend>Run only on these days</legend>
                                {DAYS.map((day, index) => <label key={day}>
                                    <input type="checkbox" aria-label={day} checked={settings.schedule.weekdays.includes(index)}
                                        onChange={() => updateSchedule({ weekdays: settings.schedule.weekdays.includes(index)
                                            ? settings.schedule.weekdays.filter(value => value !== index)
                                            : [...settings.schedule.weekdays, index].sort() })} />
                                    <span>{day.slice(0, 3)}</span>
                                </label>)}
                            </fieldset>
                            <label>Schedule timezone
                                <input type="text" required value={settings.schedule.timezone} list="admin-timezones"
                                    onChange={event => updateSchedule({ timezone: event.target.value })} />
                                <datalist id="admin-timezones"><option value="UTC" /><option value="America/New_York" />
                                    <option value="America/Chicago" /><option value="America/Denver" />
                                    <option value="America/Los_Angeles" /><option value="Europe/London" /></datalist>
                            </label>
                            <p className="admin-help">Either an interval or a clock time can trigger a run on the selected days.
                                With neither set, those days run at midnight. Manual scrapes ignore day restrictions.</p>
                        </section>
                        <section className="admin-section" aria-labelledby="admin-companies-title">
                            <div className="admin-section-heading">
                                <h3 id="admin-companies-title">Companies <span>{settings.companies.length} / {companies.length}</span></h3>
                                <div className="admin-selection-actions">
                                    <button type="button" onClick={() => setSettings({ ...settings, companies: companies.map(company => company.name) })}>Select all</button>
                                    <button type="button" onClick={() => setSettings({ ...settings, companies: [] })}>Clear all</button>
                                </div>
                            </div>
                            <input type="search" aria-label="Find a company" placeholder="Find a company"
                                value={search} onChange={event => setSearch(event.target.value)} />
                            <div className="admin-company-list">
                                {filteredCompanies.map(company => <label key={company.name} className="admin-company">
                                    <input type="checkbox" checked={settings.companies.includes(company.name)}
                                        onChange={() => toggleCompany(company.name)} />
                                    <span>{company.name}</span><small>{company.location}</small>
                                </label>)}
                                {!filteredCompanies.length ? <p>No companies match this search.</p> : null}
                            </div>
                        </section>
                    </fieldset>
                    <footer className="admin-save-bar">
                        <div role="status">{notice || (dirty ? 'Unsaved changes' : 'Settings are saved in the backend.')}</div>
                        <button type="submit" className="admin-primary" disabled={saving || !dirty}>
                            {saving ? 'Saving...' : 'Save changes'}
                        </button>
                    </footer>
                </form>
            </> : null}
        </aside>
    </>;
};

export default AdminPanel;
