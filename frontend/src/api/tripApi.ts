import type { Place, ServerStatus, TripPlan, TripPlanRequest } from '../types/api';
import { request } from './http';

export const tripApi = {
    planTrip: (body: TripPlanRequest) =>
        request<TripPlan>('/trips/plan', { method: 'POST', body: JSON.stringify(body) }),

    suggestPlaces: (query: string, signal?: AbortSignal) =>
        request<Place[]>(`/places/suggest?q=${encodeURIComponent(query)}`, { signal }),

    status: () => request<ServerStatus>('/health'),
};