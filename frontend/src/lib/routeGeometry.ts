import type { RouteOption } from '../types/api';

export type LatLng = [number, number];

// The whole route as one line (the API sends it split into risk-colored segments).
export function routeLine(route: RouteOption): LatLng[] {
    return route.segments.flatMap((segment, index) => (index === 0 ? segment.path : segment.path.slice(1)));
}