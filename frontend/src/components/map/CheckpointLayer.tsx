import { memo } from 'react';
import { CircleMarker, Tooltip } from 'react-leaflet';
import { formatDateTime } from '../../lib/format';
import { riskColor } from '../../lib/risk';
import type { Checkpoint, RouteOption } from '../../types/api';

interface Props {
    routes: RouteOption[];
    selectedId: string;
}

function CheckpointDetails({ route, checkpoint }: { route: RouteOption; checkpoint: Checkpoint }) {
    const { weather } = checkpoint;
    return (
        <>
            <strong>
                {route.name}, mile {Math.round(checkpoint.mile)}
            </strong>
            <br />
            Arrives {formatDateTime(checkpoint.eta)}
            <br />
            Wind {Math.round(weather.wind_mph)} mph, rain {weather.rain_in_hr.toFixed(2)} in/hr, snow {weather.snow_in_hr.toFixed(1)} in/hr
            <br />
            <strong style={{ color: riskColor(checkpoint.risk_level) }}>{checkpoint.risk_label}</strong>
            {checkpoint.reasons.map((reason) => (
                <div key={reason}>{reason}</div>
            ))}
        </>
    );
}

// Every checkpoint of every route; the selected route's are larger and drawn last (on top).
export const CheckpointLayer = memo(function CheckpointLayer({ routes, selectedId }: Props) {
    const ordered = [...routes].sort((a, b) => Number(a.id === selectedId) - Number(b.id === selectedId));

    return (
        <>
            {ordered.map((route) => {
                const isSelected = route.id === selectedId;
                return route.checkpoints.map((checkpoint) => (
                    <CircleMarker
                        key={`${route.id}-${checkpoint.mile}-${isSelected}`}
                        center={[checkpoint.lat, checkpoint.lng]}
                        radius={isSelected ? 5.5 : 3.5}
                        pathOptions={{
                            color: '#fff',
                            weight: isSelected ? 1.5 : 1,
                            fillColor: riskColor(checkpoint.risk_level),
                            fillOpacity: isSelected ? 1 : 0.7,
                        }}
                    >
                        <Tooltip>
                            <CheckpointDetails route={route} checkpoint={checkpoint} />
                        </Tooltip>
                    </CircleMarker>
                ));
            })}
        </>
    );
});