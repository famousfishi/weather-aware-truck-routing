import SwapVertIcon from '@mui/icons-material/SwapVert';
import {
    Box,
    Button,
    CircularProgress,
    IconButton,
    Paper,
    Stack,
    TextField,
    ToggleButton,
    ToggleButtonGroup,
    Tooltip,
    Typography,
} from '@mui/material';
import { type SubmitEvent, useState } from 'react';
import { nextFullHour, toLocalInputValue } from '../lib/format';
import type { LocationInput, SampleInterval, TripPlanRequest } from '../types/api';

interface Props {
    loading: boolean;
    onSubmit: (request: TripPlanRequest) => void;
}

function loadHint(weightLb: number): string {
    if (weightLb > 40_000) return 'Heavy load: 35–44 mph wind counts as Severe, 45+ mph as No Travel.';
    if (weightLb > 30_000) return 'At this weight, 45–54 mph wind counts as No Travel.';
    return 'Loads over 30,000 lb are treated as riskier in strong wind.';
}

export function TripForm({ loading, onSubmit }: Props) {
    const [origin, setOrigin] = useState<LocationInput>({ query: '' });
    const [destination, setDestination] = useState<LocationInput>({ query: '' });
    const [departure, setDeparture] = useState(() => toLocalInputValue(nextFullHour()));
    const [loadWeight, setLoadWeight] = useState('42000');
    const [sampleInterval, setSampleInterval] = useState<SampleInterval>(25);

    const weight = Number(loadWeight);
    const isValid = origin.query.trim() !== '' && destination.query.trim() !== '' && departure !== '' && weight > 0;

    const submit = (event: SubmitEvent) => {
        event.preventDefault();
        if (!isValid || loading) return;
        onSubmit({
            origin,
            destination,
            departure_time: new Date(departure).toISOString(),
            load_weight_lb: Math.round(weight),
            sample_interval_miles: sampleInterval,
        });
    };

    const swapPlaces = () => {
        setOrigin(destination);
        setDestination(origin);
    };

    const fillExample = () => {
        setOrigin({ query: 'Denver, CO' });
        setDestination({ query: 'Chicago, IL' });
        setLoadWeight('42000');
    };

    return (
        <Paper variant="outlined" component="form" onSubmit={submit} sx={{ p: 2 }}>
            <Stack direction="row" alignItems="baseline" justifyContent="space-between" mb={1.5}>
                <Typography variant="h2">Plan a trip</Typography>
                <Button size="small" onClick={fillExample} disabled={loading}>
                    Use an example
                </Button>
            </Stack>

            <Stack spacing={1.5}>
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 1, alignItems: 'center' }}>
                    <Stack spacing={1.5}>
                        <TextField
                            label="From"
                            placeholder="City, address or depot"
                            value={origin.query}
                            onChange={(e) => setOrigin({ query: e.target.value })}
                            disabled={loading}
                            required
                        />
                        <TextField
                            label="To"
                            placeholder="City, address or depot"
                            value={destination.query}
                            onChange={(e) => setDestination({ query: e.target.value })}
                            disabled={loading}
                            required
                        />
                    </Stack>
                    <Tooltip title="Swap from and to">
                        <span>
                            <IconButton onClick={swapPlaces} disabled={loading} aria-label="Swap from and to">
                                <SwapVertIcon />
                            </IconButton>
                        </span>
                    </Tooltip>
                </Box>

                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 9.5rem' }, gap: 1.5 }}>
                    <TextField
                        label="Departure"
                        type="datetime-local"
                        value={departure}
                        onChange={(e) => setDeparture(e.target.value)}
                        disabled={loading}
                        required
                        slotProps={{ inputLabel: { shrink: true } }}
                    />
                    <TextField
                        label="Load weight (lb)"
                        type="number"
                        value={loadWeight}
                        onChange={(e) => setLoadWeight(e.target.value)}
                        disabled={loading}
                        required
                        slotProps={{ htmlInput: { min: 1, max: 80000, step: 1 } }}
                    />
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ mt: '6px !important' }}>
                    {loadHint(weight)}
                </Typography>

                <Box>
                    <Typography variant="body2" color="text.secondary" id="interval-label" mb={0.5}>
                        Check the weather every
                    </Typography>
                    <ToggleButtonGroup
                        exclusive
                        fullWidth
                        size="small"
                        value={sampleInterval}
                        onChange={(_, value: SampleInterval | null) => value && setSampleInterval(value)}
                        aria-labelledby="interval-label"
                        disabled={loading}
                    >
                        {([10, 25, 50] as SampleInterval[]).map((miles) => (
                            <ToggleButton key={miles} value={miles} sx={{ fontWeight: 700 }}>
                                {miles} mi
                            </ToggleButton>
                        ))}
                    </ToggleButtonGroup>
                </Box>

                <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={!isValid || loading}
                    startIcon={loading ? <CircularProgress size={18} color="inherit" /> : undefined}
                >
                    {loading ? 'Checking the weather along 3 routes' : 'Find the safest route'}
                </Button>
            </Stack>
        </Paper>
    );
}