import { useEffect, useState } from 'react';
import { tripApi } from '../api/tripApi';

// True when the server runs on built-in demo data instead of the live APIs.
export function useDemoMode(): boolean {
    const [demoMode, setDemoMode] = useState(false);

    useEffect(() => {
        tripApi
            .status()
            .then((status) => setDemoMode(status.demo_mode))
            .catch(() => setDemoMode(false));
    }, []);

    return demoMode;
}