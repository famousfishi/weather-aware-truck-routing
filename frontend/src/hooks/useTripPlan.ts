import { useCallback, useState } from 'react';
import { tripApi } from '../api/tripApi';
import type { TripPlan, TripPlanRequest } from '../types/api';

// Holds the current plan plus loading/error state. Keeps the last good plan on screen if a new request fails.
export function useTripPlan() {
    const [plan, setPlan] = useState<TripPlan | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const planTrip = useCallback(async (body: TripPlanRequest) => {
        setLoading(true);
        setError(null);
        try {
            setPlan(await tripApi.planTrip(body));
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    }, []);

    const clearError = useCallback(() => setError(null), []);

    return { plan, loading, error, planTrip, clearError };
}