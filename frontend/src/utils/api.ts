export function apiUrl(path = ''): string {
    const base = process.env.REACT_APP_API_URL
        || `${window.location.protocol}//${window.location.hostname}:5000/api`;
    return base.replace(/\/$/, '') + path;
}

export async function requestJson<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(apiUrl(path), options);
    let data: T & { error?: string };
    try {
        data = await response.json();
    } catch {
        throw new Error(`The API returned an unreadable response (${response.status}). Check the backend logs.`);
    }
    if (!response.ok) {
        throw new Error(data.error || `The API request failed (${response.status}).`);
    }
    return data;
}
