import type { RouteOption } from '../types/api';

export type LatLng = [number, number];

const EARTH_RADIUS_MILES = 3958.8;

function distanceMiles([lat1, lng1]: LatLng, [lat2, lng2]: LatLng): number {
    const toRad = (deg: number) => (deg * Math.PI) / 180;
    const h =
        Math.sin(toRad(lat2 - lat1) / 2) ** 2 +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(toRad(lng2 - lng1) / 2) ** 2;
    return 2 * EARTH_RADIUS_MILES * Math.asin(Math.sqrt(h));
}

// The whole route as one line (the API sends it split into risk-colored segments).
export function routeLine(route: RouteOption): LatLng[] {
    return route.segments.flatMap((segment, index) => (index === 0 ? segment.path : segment.path.slice(1)));
}

export interface MeasuredLine {
    points: LatLng[];
    miles: number[];
}

export function measureLine(points: LatLng[]): MeasuredLine {
    const miles = [0];
    for (let i = 1; i < points.length; i++) miles.push(miles[i - 1] + distanceMiles(points[i - 1], points[i]));
    return { points, miles };
}

function interpolate(x: number, xs: number[], ys: number[]): number {
    if (x <= xs[0]) return ys[0];
    if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
    let i = 1;
    while (xs[i] < x) i++;
    const t = (x - xs[i - 1]) / (xs[i] - xs[i - 1] || 1);
    return ys[i - 1] + (ys[i] - ys[i - 1]) * t;
}

function pointAtMile(line: MeasuredLine, mile: number): LatLng {
    return [
        interpolate(mile, line.miles, line.points.map((p) => p[0])),
        interpolate(mile, line.miles, line.points.map((p) => p[1])),
    ];
}

// Where the truck is at `time`, following the road (not a straight line between checkpoints).
export function truckPositionAt(route: RouteOption, line: MeasuredLine, time: number): LatLng {
    const times = route.checkpoints.map((c) => Date.parse(c.eta));
    const checkpointMiles = route.checkpoints.map((c) => c.mile);
    const mile = interpolate(time, times, checkpointMiles);
    const lastCheckpointMile = checkpointMiles[checkpointMiles.length - 1] || 1;
    return pointAtMile(line, (mile / lastCheckpointMile) * line.miles[line.miles.length - 1]);
}