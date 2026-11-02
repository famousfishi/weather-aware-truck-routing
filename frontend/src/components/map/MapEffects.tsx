import L from 'leaflet';
import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import { routeLine } from '../../lib/routeGeometry';
import type { Checkpoint, TripPlan } from '../../types/api';

// Zooms the map to show every route whenever a new plan arrives.
export function FitToPlan({ plan }: { plan: TripPlan }) {
    const map = useMap();

    useEffect(() => {
        const bounds = L.latLngBounds(plan.routes.flatMap(routeLine));
        if (bounds.isValid()) map.fitBounds(bounds, { padding: [56, 56] });
    }, [map, plan]);

    return null;
}

// Moves the map to a checkpoint picked in the table.
export function FlyToCheckpoint({ checkpoint }: { checkpoint: Checkpoint | null }) {
    const map = useMap();

    useEffect(() => {
        if (checkpoint) map.flyTo([checkpoint.lat, checkpoint.lng], Math.max(map.getZoom(), 8), { duration: 0.6 });
    }, [map, checkpoint]);

    return null;
}