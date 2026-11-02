import { Box, ButtonBase, Paper, Stack, Typography } from '@mui/material';
import { memo } from 'react';
import { formatDuration, formatMiles, formatTime } from '../lib/format';
import { riskColor } from '../lib/risk';
import { colors } from '../theme';
import type { RiskLevel, RouteOption } from '../types/api';
import { RiskBar } from './RiskBar';
import { RouteShield } from './RouteShield';

interface Props {
    route: RouteOption;
    selected: boolean;
    onSelect: (routeId: string) => void;
}

function Stat({ label, value }: { label: string; value: string }) {
    return (
        <Box>
            <Typography variant="caption" color="text.secondary" component="div">
                {label}
            </Typography>
            <Typography sx={{ fontWeight: 700, fontSize: '0.9375rem' }}>{value}</Typography>
        </Box>
    );
}

// The four numbers the ranking uses, in the order it uses them.
function RankingFigure({ label, value, level }: { label: string; value: string; level?: RiskLevel }) {
    return (
        <Stack direction="row" spacing={0.6} alignItems="center">
            {level !== undefined && <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: riskColor(level), flexShrink: 0 }} />}
            <Typography variant="caption" color="text.secondary" noWrap>
                {label} <Box component="strong" sx={{ color: 'text.primary' }}>{value}</Box>
            </Typography>
        </Stack>
    );
}

export const RouteCard = memo(function RouteCard({ route, selected, onSelect }: Props) {
    const { summary } = route;

    return (
        <Paper
            variant="outlined"
            sx={{
                overflow: 'hidden',
                outline: selected ? `2px solid ${colors.interstateBlue}` : 'none',
                outlineOffset: -1,
                transition: 'outline-color 120ms',
            }}
        >
            <ButtonBase
                onClick={() => onSelect(route.id)}
                aria-pressed={selected}
                sx={{ display: 'block', width: '100%', textAlign: 'left', p: 1.5, '&:hover': { bgcolor: 'rgba(27,79,156,0.04)' } }}
            >
                <Stack direction="row" alignItems="center" spacing={1.25}>
                    <RouteShield letter={route.id} size={30} />
                    <Box flex={1} minWidth={0}>
                        <Typography variant="h3">{route.name}</Typography>
                        <Typography variant="body2" color="text.secondary" noWrap>
                            {route.via.length ? `via ${route.via.join(', ')}` : 'via local and state roads'}
                        </Typography>
                    </Box>
                    {route.is_recommended ? (
                        <Box sx={{ bgcolor: colors.guideSignGreen, color: '#fff', px: 1, py: 0.25, borderRadius: 1, fontSize: 12, fontWeight: 700 }}>
                            Recommended
                        </Box>
                    ) : (
                        <Typography variant="caption" color="text.secondary" fontWeight={600}>
                            Rank {route.rank}
                        </Typography>
                    )}
                </Stack>

                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 1, my: 1.25 }}>
                    <Stat label="Distance" value={formatMiles(route.distance_miles)} />
                    <Stat label="Drive time" value={formatDuration(route.duration_seconds)} />
                    <Stat label="Arrives" value={formatTime(route.arrival_time)} />
                </Box>

                <RiskBar summary={summary} />

                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', columnGap: 1.5, rowGap: 0.25, mt: 1 }}>
                    <RankingFigure label="No-Travel" value={formatMiles(summary.no_travel_miles)} level={4} />
                    <RankingFigure label="Severe" value={formatMiles(summary.severe_miles)} level={3} />
                    <RankingFigure label="High" value={formatMiles(summary.high_miles)} level={2} />
                    <RankingFigure label="Average risk" value={`${summary.average_risk.toFixed(2)} of 4`} />
                </Box>
            </ButtonBase>
        </Paper>
    );
});