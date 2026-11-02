import { Box, Tooltip } from '@mui/material';
import { formatMiles } from '../lib/format';
import { RISK_LEVELS } from '../lib/risk';
import type { RouteSummary } from '../types/api';

export function milesByLevel(summary: RouteSummary): number[] {
    return [summary.low_miles, summary.moderate_miles, summary.high_miles, summary.severe_miles, summary.no_travel_miles];
}

// One bar per route: how many of its miles fall in each risk level.
export function RiskBar({ summary }: { summary: RouteSummary }) {
    const miles = milesByLevel(summary);
    const total = miles.reduce((sum, value) => sum + value, 0) || 1;

    return (
        <Box
            sx={{ display: 'flex', height: 10, borderRadius: 5, overflow: 'hidden', bgcolor: 'divider' }}
            role="img"
            aria-label={RISK_LEVELS.map((r, i) => `${r.label} ${formatMiles(miles[i])}`).join(', ')}
        >
            {RISK_LEVELS.map(({ level, label, color }) =>
                miles[level] > 0 ? (
                    <Tooltip key={level} title={`${label}: ${formatMiles(miles[level])}`}>
                        <Box sx={{ width: `${(miles[level] / total) * 100}%`, bgcolor: color }} />
                    </Tooltip>
                ) : null,
            )}
        </Box>
    );
}