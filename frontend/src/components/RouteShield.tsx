import { Box } from '@mui/material';
import { colors } from '../theme';

// An interstate-style shield with the route letter. Returned as markup so the map can reuse it in its icons.
export function shieldMarkup(letter: string, size: number): string {
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 26 28" width="${size}" height="${Math.round((size * 28) / 26)}" aria-hidden="true">
    <path d="M2 1h20c1.3 2.7 2 5.6 2 8.7C24 17.2 18.8 22.6 12 25 5.2 22.6 0 17.2 0 9.7 0 6.6.7 3.7 2 1z" fill="${colors.interstateBlue}" stroke="#fff" stroke-width="1.6"/>
    <path d="M2.9 2.3h18.2c.5 1.1.9 2.3 1.2 3.7H1.7c.3-1.4.7-2.6 1.2-3.7z" fill="${colors.shieldRed}"/>
    <text x="12" y="18.6" text-anchor="middle" font-family="Overpass, sans-serif" font-weight="800" font-size="11.5" fill="#fff">${letter}</text>
  </svg>`;
}

export function RouteShield({ letter, size = 28 }: { letter: string; size?: number }) {
    return (
        <Box
            component="span"
            sx={{ display: 'inline-flex', flexShrink: 0, lineHeight: 0 }}
            role="img"
            aria-label={`Route ${letter}`}
            dangerouslySetInnerHTML={{ __html: shieldMarkup(letter, size) }}
        />
    );
}