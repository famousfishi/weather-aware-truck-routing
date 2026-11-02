import type { RiskLevel } from '../types/api';

// Colors follow the weather-radar scale drivers already know: green, yellow, orange, red, magenta.
export const RISK_LEVELS: { level: RiskLevel; label: string; color: string; heatOpacity: number }[] = [
    { level: 0, label: 'Low', color: '#2E9E5B', heatOpacity: 0.1 },
    { level: 1, label: 'Moderate', color: '#E0A800', heatOpacity: 0.34 },
    { level: 2, label: 'High', color: '#EF7A1A', heatOpacity: 0.44 },
    { level: 3, label: 'Severe', color: '#D62F2F', heatOpacity: 0.52 },
    { level: 4, label: 'No Travel', color: '#B4239C', heatOpacity: 0.6 },
];

export const riskColor = (level: RiskLevel) => RISK_LEVELS[level].color;
export const riskLabel = (level: RiskLevel) => RISK_LEVELS[level].label;