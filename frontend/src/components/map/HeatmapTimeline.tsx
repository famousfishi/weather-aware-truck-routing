import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { Box, FormControlLabel, IconButton, Paper, Slider, Stack, Switch, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { formatDateTime } from '../../lib/format';

interface Props {
    startTime: string;
    hours: number;
    hour: number;
    onHourChange: (hour: number) => void;
    showHeatmap: boolean;
    onShowHeatmapChange: (show: boolean) => void;
}

const PLAY_STEP_MS = 650;
const MARKS = [0, 12, 24, 36, 48].map((value) => ({ value, label: value === 0 ? 'Departure' : `+${value}h` }));

// The 0–48 hour forecast slider. Play steps through the hours so the storm (and the truck) move.
export function HeatmapTimeline({ startTime, hours, hour, onHourChange, showHeatmap, onShowHeatmapChange }: Props) {
    const [playing, setPlaying] = useState(false);

    useEffect(() => {
        if (!playing) return;
        if (hour >= hours) {
            setPlaying(false);
            return;
        }
        const timer = window.setTimeout(() => onHourChange(hour + 1), PLAY_STEP_MS);
        return () => window.clearTimeout(timer);
    }, [playing, hour, hours, onHourChange]);

    const togglePlay = () => {
        if (!playing && hour >= hours) onHourChange(0);
        setPlaying(!playing);
    };

    const time = Date.parse(startTime) + hour * 3_600_000;

    return (
        <Paper
            variant="outlined"
            sx={{
                position: 'absolute',
                zIndex: 1000,
                left: { xs: 8, md: '50%' },
                right: { xs: 8, md: 'auto' },
                bottom: 24,
                transform: { md: 'translateX(-50%)' },
                width: { md: 600 },
                px: 2,
                pt: 1.25,
                pb: 0.5,
                boxShadow: '0 4px 18px rgba(26,36,33,0.16)',
            }}
        >
            <Stack direction="row" alignItems="center" spacing={1.5}>
                <IconButton
                    onClick={togglePlay}
                    aria-label={playing ? 'Pause forecast animation' : 'Play forecast animation'}
                    sx={{ bgcolor: 'primary.main', color: '#fff', '&:hover': { bgcolor: 'primary.dark' } }}
                    size="small"
                >
                    {playing ? <PauseIcon /> : <PlayArrowIcon />}
                </IconButton>
                <Box flex={1} minWidth={0}>
                    <Typography sx={{ fontWeight: 800, fontSize: '1rem' }} aria-live="polite">
                        Weather at {formatDateTime(time)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" component="div" noWrap>
                        {hour === 0 ? 'At departure' : `${hour} h after departure`}. The truck marks where you would be.
                    </Typography>
                </Box>
                <FormControlLabel
                    control={<Switch size="small" checked={showHeatmap} onChange={(e) => onShowHeatmapChange(e.target.checked)} />}
                    label={<Typography variant="body2">Heatmap</Typography>}
                    sx={{ mr: 0 }}
                />
            </Stack>
            <Box px={1}>
                <Slider
                    value={hour}
                    min={0}
                    max={hours}
                    step={1}
                    marks={MARKS}
                    onChange={(_, value) => {
                        setPlaying(false);
                        onHourChange(value as number);
                    }}
                    aria-label="Hours after departure"
                    getAriaValueText={(value) => `${value} hours after departure`}
                    sx={{ '& .MuiSlider-markLabel': { fontSize: 12 } }}
                />
            </Box>
        </Paper>
    );
}