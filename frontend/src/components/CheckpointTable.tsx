import { Box, Paper, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { memo } from 'react';
import { formatTime } from '../lib/format';
import { riskColor } from '../lib/risk';
import type { Checkpoint, RouteOption } from '../types/api';

interface Props {
    route: RouteOption;
    intervalMiles: number;
    onFocusCheckpoint: (checkpoint: Checkpoint) => void;
}

export const CheckpointTable = memo(function CheckpointTable({ route, intervalMiles, onFocusCheckpoint }: Props) {
    return (
        <Paper variant="outlined">
            <Box sx={{ px: 1.5, pt: 1.5, pb: 1 }}>
                <Typography variant="h3">Checkpoints on {route.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                    Weather every {intervalMiles} miles, at the time the truck gets there. Wind in mph, rain and snow in
                    inches per hour. Select a row to see it on the map.
                </Typography>
            </Box>
            <Box sx={{ maxHeight: 340, overflow: 'auto' }}>
                <Table
                    size="small"
                    stickyHeader
                    aria-label={`Weather checkpoints on ${route.name}`}
                    sx={{ '& th, & td': { px: 1 }, '& th:first-of-type, & td:first-of-type': { pl: 1.5 } }}
                >
                    <TableHead>
                        <TableRow>
                            <TableCell>Mile</TableCell>
                            <TableCell>Arrives</TableCell>
                            <TableCell align="right">Wind</TableCell>
                            <TableCell align="right">Rain</TableCell>
                            <TableCell align="right">Snow</TableCell>
                            <TableCell>Risk</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {route.checkpoints.map((checkpoint) => (
                            <TableRow
                                key={checkpoint.mile}
                                hover
                                tabIndex={0}
                                onClick={() => onFocusCheckpoint(checkpoint)}
                                onKeyDown={(e) => e.key === 'Enter' && onFocusCheckpoint(checkpoint)}
                                sx={{ cursor: 'pointer', '& td': { whiteSpace: 'nowrap' } }}
                                title={checkpoint.reasons.join('\n') || undefined}
                            >
                                <TableCell>{Math.round(checkpoint.mile)}</TableCell>
                                <TableCell>{formatTime(checkpoint.eta)}</TableCell>
                                <TableCell align="right">{Math.round(checkpoint.weather.wind_mph)}</TableCell>
                                <TableCell align="right">{checkpoint.weather.rain_in_hr.toFixed(2)}</TableCell>
                                <TableCell align="right">{checkpoint.weather.snow_in_hr.toFixed(1)}</TableCell>
                                <TableCell>
                                    <Stack direction="row" spacing={0.75} alignItems="center">
                                        <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: riskColor(checkpoint.risk_level) }} />
                                        <span>{checkpoint.risk_label}</span>
                                    </Stack>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Box>
        </Paper>
    );
});