import type { Place, ServerStatus, TripPlan, TripPlanRequest, WeatherBatch, WeatherRequest } from '../types/api';
import { ApiError, request } from './http';
import { fetchForecasts } from './openMeteo';

const MAX_ATTEMPTS = 3;

// Plans a trip. In browser-weather mode the server first answers 428 with the forecasts it needs; we download them
// and ask again with them attached. In normal mode the first answer is already the plan.
async function planTrip(body: TripPlanRequest): Promise<TripPlan> {
    let weather: WeatherBatch[] = [];
    for (let attempt = 1; ; attempt++) {
        try {
            return await request<TripPlan>('/trips/plan', { method: 'POST', body: JSON.stringify({ ...body, weather }) });
        } catch (error) {
            if (!(error instanceof ApiError) || error.status !== 428 || attempt === MAX_ATTEMPTS) throw error;
            const { weather_requests } = error.body as { weather_requests: WeatherRequest[] };
            weather = [...weather, ...(await fetchForecasts(weather_requests))];
        }
    }
}

export const tripApi = {
    planTrip,

    suggestPlaces: (query: string, signal?: AbortSignal) =>
        request<Place[]>(`/places/suggest?q=${encodeURIComponent(query)}`, { signal }),

    status: () => request<ServerStatus>('/health'),
};