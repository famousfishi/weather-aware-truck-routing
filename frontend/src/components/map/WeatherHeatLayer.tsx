import L from 'leaflet';
import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import { RISK_LEVELS } from '../../lib/risk';
import type { HeatCell, Heatmap } from '../../types/api';

const HEAT_PANE = 'weather-heat';

interface Props {
    heatmap: Heatmap;
    hour: number;
    visible: boolean;
}

function cellTooltip(cell: HeatCell, hour: number): string {
    const level = RISK_LEVELS[cell.risk_level[hour]];
    return `<strong style="color:${level.color}">${level.label}</strong><br>
    Wind ${cell.wind_mph[hour]} mph<br>Rain ${cell.rain_in_hr[hour].toFixed(2)} in/hr<br>Snow ${cell.snow_in_hr[hour].toFixed(1)} in/hr`;
}

/**
 * Draws the heatmap cells once on a single <canvas> (fast for hundreds of shapes), then only
 * recolors them when the slider moves. A light CSS blur on the layer blends the square cells
 * into a smooth weather surface without changing their colors.
 */
export function WeatherHeatLayer({ heatmap, hour, visible }: Props) {
    const map = useMap();
    const cellsRef = useRef<L.Rectangle[]>([]);
    const hourRef = useRef(hour);
    hourRef.current = hour;

    useEffect(() => {
        const pane = map.getPane(HEAT_PANE) ?? map.createPane(HEAT_PANE);
        pane.style.zIndex = '350';
        pane.style.filter = 'blur(6px)';

        const renderer = L.canvas({ pane: HEAT_PANE, padding: 0.5 });
        const half = heatmap.cell_size_deg / 2;
        const group = L.layerGroup().addTo(map);

        cellsRef.current = heatmap.cells.map((cell) =>
            L.rectangle(
                [
                    [cell.lat - half, cell.lng - half],
                    [cell.lat + half, cell.lng + half],
                ],
                { renderer, stroke: false, fillOpacity: 0 },
            )
                .bindTooltip(() => cellTooltip(cell, hourRef.current), { sticky: true })
                .addTo(group),
        );

        return () => {
            group.remove();
            cellsRef.current = [];
        };
    }, [map, heatmap]);

    useEffect(() => {
        const pane = map.getPane(HEAT_PANE);
        if (pane) pane.style.display = visible ? '' : 'none';

        cellsRef.current.forEach((rectangle, index) => {
            const level = RISK_LEVELS[heatmap.cells[index].risk_level[hour]];
            rectangle.setStyle({ fillColor: level.color, fillOpacity: level.heatOpacity });
        });
    }, [map, heatmap, hour, visible]);

    return null;
}