const timeFormat = new Intl.DateTimeFormat(undefined, { weekday: 'short', hour: 'numeric', minute: '2-digit' });
const dateTimeFormat = new Intl.DateTimeFormat(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
});

export const formatTime = (value: string | number | Date) => timeFormat.format(new Date(value));
export const formatDateTime = (value: string | number | Date) => dateTimeFormat.format(new Date(value));
export const formatMiles = (miles: number) => `${Math.round(miles).toLocaleString()} mi`;

export function formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours ? `${hours}h ${String(minutes).padStart(2, '0')}m` : `${minutes} min`;
}

// <input type="datetime-local"> wants "YYYY-MM-DDTHH:mm" in the user's local time.
export function toLocalInputValue(date: Date): string {
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function nextFullHour(): Date {
    const date = new Date();
    date.setHours(date.getHours() + 1, 0, 0, 0);
    return date;
}