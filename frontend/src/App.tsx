import { AppBar, Box, Stack, Toolbar, Typography } from '@mui/material';

export default function App() {
    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <AppBar position="static" color="inherit" sx={{ borderBottom: 1, borderColor: 'divider' }} elevation={0}>
                <Toolbar variant="dense" sx={{ gap: 1.25 }}>
                    <Typography variant="h1" component="h1">
                        Weather-Aware Truck Routing
                    </Typography>
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
                        <Typography variant="body2" color="text.secondary">
                            The trip form goes here.
                        </Typography>
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