import { CircleMarker, MapContainer, TileLayer, Tooltip } from 'react-leaflet';
import { colors } from '../../theme';
import type { Checkpoint, Place, TripPlan } from '../../types/api';
import { CheckpointLayer } from './CheckpointLayer';
import { FitToPlan, FlyToCheckpoint } from './MapEffects';
import { RouteLayers } from './RouteLayers';
import { TruckMarker } from './TruckMarker';
import { WeatherHeatLayer } from './WeatherHeatLayer';

interface Props {
    plan: TripPlan | null;
    selectedRouteId: string;
    onSelectRoute: (routeId: string) => void;
    heatmapHour: number;
    showHeatmap: boolean;
    focusedCheckpoint: Checkpoint | null;
}

function Endpoint({ place, label }: { place: Place; label: string }) {
    return (
        <CircleMarker center={[place.lat, place.lng]} radius={7} pathOptions={{ color: '#fff', weight: 2.5, fillColor: colors.ink, fillOpacity: 1 }}>
            <Tooltip permanent direction="top" offset={[0, -8]} className="endpoint-label">
                {label}: {place.label}
            </Tooltip>
        </CircleMarker>
    );
}

export function TripMap({ plan, selectedRouteId, onSelectRoute, heatmapHour, showHeatmap, focusedCheckpoint }: Props) {
    const selectedRoute = plan?.routes.find((route) => route.id === selectedRouteId);
    const heatmapTime = plan ? Date.parse(plan.heatmap.start_time) + heatmapHour * 3_600_000 : 0;

    return (
        <MapContainer center={[39.5, -98.35]} zoom={4} minZoom={3} style={{ height: '100%', width: '100%' }}>
            <TileLayer
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                maxZoom={19}
            />
            {plan && (
                <>
                    <FitToPlan plan={plan} />
                    <FlyToCheckpoint checkpoint={focusedCheckpoint} />
                    <WeatherHeatLayer heatmap={plan.heatmap} hour={heatmapHour} visible={showHeatmap} />
                    <RouteLayers routes={plan.routes} selectedId={selectedRouteId} onSelect={onSelectRoute} />
                    <CheckpointLayer routes={plan.routes} selectedId={selectedRouteId} />
                    <Endpoint place={plan.origin} label="Start" />
                    <Endpoint place={plan.destination} label="End" />
                    {selectedRoute && <TruckMarker route={selectedRoute} time={heatmapTime} />}
                </>
            )}
        </MapContainer>
    );
}