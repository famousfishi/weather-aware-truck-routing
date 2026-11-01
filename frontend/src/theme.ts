import { createTheme } from '@mui/material/styles';

// Overpass is an open-source cousin of the lettering on US highway signs.
export const colors = {
    interstateBlue: '#1B4F9C',
    shieldRed: '#C8102E',
    guideSignGreen: '#006B45',
    ink: '#1A2421',
    road: '#F1F3F2',
    line: '#D9DEDB',
    muted: '#5B6762',
};

export const theme = createTheme({
    palette: {
        primary: { main: colors.interstateBlue },
        success: { main: colors.guideSignGreen },
        text: { primary: colors.ink, secondary: colors.muted },
        background: { default: colors.road, paper: '#FFFFFF' },
        divider: colors.line,
    },
    typography: {
        fontFamily: '"Overpass", "Segoe UI", system-ui, sans-serif',
        h1: { fontSize: '1.125rem', fontWeight: 800, letterSpacing: '0.01em' },
        h2: { fontSize: '1rem', fontWeight: 700 },
        h3: { fontSize: '0.9375rem', fontWeight: 700 },
        body1: { fontSize: '0.9375rem', lineHeight: 1.5 },
        body2: { fontSize: '0.8125rem', lineHeight: 1.45 },
        caption: { fontSize: '0.75rem', lineHeight: 1.4 },
        button: { textTransform: 'none', fontWeight: 700, letterSpacing: '0.01em' },
    },
    shape: { borderRadius: 6 },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: { fontVariantNumeric: 'tabular-nums' },
                '@media (prefers-reduced-motion: reduce)': { '*': { transition: 'none !important', animation: 'none !important' } },
            },
        },
        MuiButton: { defaultProps: { disableElevation: true } },
        MuiPaper: { defaultProps: { elevation: 0 } },
        MuiTextField: { defaultProps: { size: 'small', fullWidth: true } },
        MuiTooltip: { defaultProps: { arrow: true } },
    },
});