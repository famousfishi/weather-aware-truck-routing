import { Alert, AppBar, Box, Chip, LinearProgress, Stack, Toolbar, Typography } from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import { CheckpointTable } from './components/CheckpointTable';
import { HeatmapTimeline } from './components/map/HeatmapTimeline';
import { RiskLegend } from './components/map/RiskLegend';
import { TripMap } from './components/map/TripMap';
import { RecommendationSign } from './components/RecommendationSign';
import { RouteCard } from './components/RouteCard';
import { RouteShield } from './components/RouteShield';
import { TripForm } from './components/TripForm';
import { useDemoMode } from './hooks/useDemoMode';
import { useTripPlan } from './hooks/useTripPlan';
import type { Checkpoint } from './types/api';

export default function App() {
    const { plan, loading, error, planTrip, clearError } = useTripPlan();
    const demoMode = useDemoMode();
    const [selectedRouteId, setSelectedRouteId] = useState('');
    const [heatmapHour, setHeatmapHour] = useState(0);
    const [showHeatmap, setShowHeatmap] = useState(true);
    const [focusedCheckpoint, setFocusedCheckpoint] = useState<Checkpoint | null>(null);

    // A new plan starts on the recommended route, at departure time.
    useEffect(() => {
        if (!plan) return;
        setSelectedRouteId(plan.recommendation.route_id);
        setHeatmapHour(0);
        setFocusedCheckpoint(null);
    }, [plan]);

    const selectRoute = useCallback((routeId: string) => setSelectedRouteId(routeId), []);
    const selectedRoute = plan?.routes.find((route) => route.id === selectedRouteId);

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
                                {selectedRoute && (
                                    <CheckpointTable route={selectedRoute} intervalMiles={plan.sample_interval_miles} onFocusCheckpoint={setFocusedCheckpoint} />
                                )}
                            </>
                        )}
                    </Stack>
                </Box>

                <Box component="main" sx={{ flex: 1, position: 'relative', minHeight: { xs: '65vh', md: 0 }, order: { xs: -1, md: 0 } }}>
                    {loading && <LinearProgress sx={{ position: 'absolute', top: 0, left: 0, right: 0, zIndex: 1100 }} />}
                    <TripMap
                        plan={plan}
                        selectedRouteId={selectedRouteId}
                        onSelectRoute={selectRoute}
                        heatmapHour={heatmapHour}
                        showHeatmap={showHeatmap}
                        focusedCheckpoint={focusedCheckpoint}
                    />
                    <RiskLegend />
                    {plan && (
                        <HeatmapTimeline
                            startTime={plan.heatmap.start_time}
                            hours={plan.heatmap.hours}
                            hour={heatmapHour}
                            onHourChange={setHeatmapHour}
                            showHeatmap={showHeatmap}
                            onShowHeatmapChange={setShowHeatmap}
                        />
                    )}
                </Box>
            </Box>
        </Box>
    );
}