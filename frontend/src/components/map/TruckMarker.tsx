import L from 'leaflet';
import { useMemo } from 'react';
import { Marker, Tooltip } from 'react-leaflet';
import { formatTime } from '../../lib/format';
import { measureLine, routeLine, truckPositionAt } from '../../lib/routeGeometry';
import { colors } from '../../theme';
import type { RouteOption } from '../../types/api';

const truckIcon = L.divIcon({
    className: 'map-icon',
    html: `<div class="truck-marker"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
    <path fill="${colors.interstateBlue}" d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9 1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
  </svg></div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
});

// Shows where the truck would be on the selected route at the heatmap's chosen hour.
export function TruckMarker({ route, time }: { route: RouteOption; time: number }) {
    const line = useMemo(() => measureLine(routeLine(route)), [route]);
    const position = truckPositionAt(route, line, time);
    const arrived = time >= Date.parse(route.arrival_time);

    return (
        <Marker position={position} icon={truckIcon} zIndexOffset={1000} keyboard={false}>
            <Tooltip direction="top" offset={[0, -14]}>
                {arrived ? `Arrived by ${formatTime(route.arrival_time)}` : `Truck on ${route.name} at ${formatTime(time)}`}
            </Tooltip>
        </Marker>
    );
}