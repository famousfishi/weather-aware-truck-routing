import { Alert, AppBar, Box, Chip, Stack, Toolbar, Typography } from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import { RecommendationSign } from './components/RecommendationSign';
import { RouteCard } from './components/RouteCard';
import { RouteShield } from './components/RouteShield';
import { TripForm } from './components/TripForm';
import { useDemoMode } from './hooks/useDemoMode';
import { useTripPlan } from './hooks/useTripPlan';

export default function App() {
    const { plan, loading, error, planTrip, clearError } = useTripPlan();
    const demoMode = useDemoMode();
    const [selectedRouteId, setSelectedRouteId] = useState('');

    // A new plan starts on the recommended route.
    useEffect(() => {
        if (plan) setSelectedRouteId(plan.recommendation.route_id);
    }, [plan]);

    const selectRoute = useCallback((routeId: string) => setSelectedRouteId(routeId), []);

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <AppBar position="static" color="inherit" sx={{ borderBottom: 1, borderColor: 'divider' }} elevation={0}>
                <Toolbar variant="dense" sx={{ gap: 1.25 }}>
                    <RouteShield letter="" size={22} />
                    <Typography variant="h1" component="h1">
                        Weather-Aware Truck Routing
                    </Typography>
                    {demoMode && <Chip size="small" color="warning" label="Demo data" sx={{ ml: 1, fontWeight: 700 }} />}
                </Toolbar>
            </AppBar>

            <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: { xs: 'column', md: 'row' } }}>
                <Box
                    component="aside"
                    sx={{
                        width: { md: 460 },
                        flexShrink: 0,
                        overflowY: { md: 'auto' },
                        borderRight: { md: 1 },
                        borderColor: { md: 'divider' },
                        p: 2,
                    }}
                >
                    <Stack spacing={2}>
                        <TripForm loading={loading} onSubmit={planTrip} />

                        {error && (
                            <Alert severity="error" onClose={clearError}>
                                {error}
                            </Alert>
                        )}

                        {!plan && !error && (
                            <Typography variant="body2" color="text.secondary" sx={{ px: 0.5 }}>
                                Enter a trip to compare three routes. Each one is checked against the forecast for the hour the
                                truck reaches every checkpoint, then ranked by Severe miles, High miles, average risk and drive time.
                            </Typography>
                        )}

                        {plan && (
                            <>
                                <RecommendationSign recommendation={plan.recommendation} />
                                <Stack spacing={1.25} component="section" aria-label="Route options">
                                    {plan.routes.map((route) => (
                                        <RouteCard key={route.id} route={route} selected={route.id === selectedRouteId} onSelect={selectRoute} />
                                    ))}
                                </Stack>
                            </>
                        )}
                    </Stack>
                </Box>

                <Box component="main" sx={{ flex: 1, position: 'relative', minHeight: { xs: '65vh', md: 0 }, order: { xs: -1, md: 0 } }}>
                    <Typography color="text.secondary" sx={{ p: 2 }}>
                        The map goes here.
                    </Typography>
                </Box>
            </Box>
        </Box>
    );
}