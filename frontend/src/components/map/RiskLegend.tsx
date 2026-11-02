import { Box, Paper, Stack, Typography } from '@mui/material';
import { RISK_LEVELS } from '../../lib/risk';

export function RiskLegend() {
    return (
        <Paper variant="outlined" sx={{ position: 'absolute', zIndex: 1000, top: 12, right: 12, px: 1.5, py: 1 }}>
            <Typography variant="caption" fontWeight={700} component="div" mb={0.5}>
                Weather risk
            </Typography>
            <Stack spacing={0.4}>
                {RISK_LEVELS.map(({ level, label, color }) => (
                    <Stack key={level} direction="row" spacing={1} alignItems="center">
                        <Box sx={{ width: 18, height: 6, borderRadius: 3, bgcolor: color }} />
                        <Typography variant="caption">{label}</Typography>
                    </Stack>
                ))}
            </Stack>
        </Paper>
    );
}