import L from 'leaflet';
import { memo, useMemo } from 'react';
import { Marker, Polyline, Tooltip } from 'react-leaflet';
import { formatDuration, formatMiles } from '../../lib/format';
import { riskColor } from '../../lib/risk';
import { routeLine } from '../../lib/routeGeometry';
import type { RouteOption } from '../../types/api';
import { shieldMarkup } from '../RouteShield';

interface Props {
    routes: RouteOption[];
    selectedId: string;
    onSelect: (routeId: string) => void;
}

function RouteSummaryTooltip({ route }: { route: RouteOption }) {
    return (
        <Tooltip sticky>
            <strong>{route.name}</strong>
            {route.is_recommended && ' (recommended)'}
            <br />
            {formatMiles(route.distance_miles)}, {formatDuration(route.duration_seconds)}
            <br />
            Severe {formatMiles(route.summary.severe_miles)}, High {formatMiles(route.summary.high_miles)}
        </Tooltip>
    );
}

// Other routes are grey; the selected one is drawn on top, colored by risk along its length.
export const RouteLayers = memo(function RouteLayers({ routes, selectedId, onSelect }: Props) {
    const lines = useMemo(() => new Map(routes.map((route) => [route.id, routeLine(route)])), [routes]);
    const selected = routes.find((route) => route.id === selectedId);

    return (
        <>
            {routes
                .filter((route) => route.id !== selectedId)
                .map((route) => (
                    <Polyline
                        key={route.id}
                        positions={lines.get(route.id)!}
                        pathOptions={{ color: '#7D8A85', weight: 5, opacity: 0.75 }}
                        eventHandlers={{ click: () => onSelect(route.id) }}
                    >
                        <RouteSummaryTooltip route={route} />
                    </Polyline>
                ))}

            {selected && (
                <>
                    <Polyline key={`${selected.id}-casing`} positions={lines.get(selected.id)!} pathOptions={{ color: '#fff', weight: 11, opacity: 1 }}>
                        <RouteSummaryTooltip route={selected} />
                    </Polyline>
                    {selected.segments.map((segment, index) => (
                        <Polyline
                            key={`${selected.id}-${index}`}
                            positions={segment.path}
                            pathOptions={{ color: riskColor(segment.risk_level), weight: 6, opacity: 1, interactive: false }}
                        />
                    ))}
                </>
            )}

            {routes.map((route) => {
                const line = lines.get(route.id)!;
                return (
                    <Marker
                        key={`shield-${route.id}`}
                        position={line[Math.floor(line.length / 2)]}
                        icon={L.divIcon({ className: 'map-icon', html: shieldMarkup(route.id, 28), iconSize: [28, 30], iconAnchor: [14, 15] })}
                        zIndexOffset={route.id === selectedId ? 500 : 0}
                        eventHandlers={{ click: () => onSelect(route.id) }}
                        title={`Select ${route.name}`}
                    />
                );
            })}
        </>
    );
});