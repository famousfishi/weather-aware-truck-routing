import { Alert, Box, Stack, Typography } from '@mui/material';
import { colors } from '../theme';
import type { Recommendation } from '../types/api';
import { RouteShield } from './RouteShield';

// Styled after a green highway guide sign: white lettering, white inset border.
export function RecommendationSign({ recommendation }: { recommendation: Recommendation }) {
    return (
        <Stack spacing={1}>
            <Box sx={{ bgcolor: colors.guideSignGreen, borderRadius: 2, p: '5px' }} role="status" aria-live="polite">
                <Box sx={{ border: '2px solid #fff', borderRadius: 1.5, px: 1.75, py: 1.5, color: '#fff' }}>
                    <Typography variant="body2" sx={{ opacity: 0.85, fontWeight: 600 }}>
                        Recommended
                    </Typography>
                    <Stack direction="row" alignItems="center" spacing={1.25} mt={0.5}>
                        <RouteShield letter={recommendation.route_id} size={34} />
                        <Typography component="p" sx={{ fontSize: '1.3rem', fontWeight: 800, lineHeight: 1.15 }}>
                            {recommendation.headline}
                        </Typography>
                    </Stack>
                    <Box component="ul" sx={{ m: 0, mt: 1.25, pl: 2.25 }}>
                        {recommendation.reasons.map((reason) => (
                            <Typography component="li" variant="body2" key={reason} sx={{ opacity: 0.95, mt: 0.25 }}>
                                {reason}
                            </Typography>
                        ))}
                    </Box>
                </Box>
            </Box>
            {recommendation.warnings.map((warning) => (
                <Alert key={warning} severity="warning" variant="outlined" sx={{ bgcolor: '#FFF8E1' }}>
                    {warning}
                </Alert>
            ))}
        </Stack>
    );
}