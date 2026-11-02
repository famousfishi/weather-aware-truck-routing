import type { WeatherBatch, WeatherRequest } from '../types/api';
import { ApiError } from './http';

// Downloads the forecasts the server asked for, straight from Open-Meteo (it allows calls from any website).
// Each visitor uses their own free daily allowance, instead of one allowance shared by every app on the host.
export function fetchForecasts(requests: WeatherRequest[]): Promise<WeatherBatch[]> {
    return Promise.all(
        requests.map(async ({ url, points }) => {
            let response: Response;
            try {
                response = await fetch(url);
            } catch {
                throw new ApiError('Could not reach the weather service. Check your connection and try again.');
            }

            const body = await response.json().catch(() => null);
            if (!response.ok) {
                throw new ApiError(`Open-Meteo weather request failed: ${body?.reason ?? `HTTP ${response.status}`}`);
            }
            return { points, body };
        }),
    );
}