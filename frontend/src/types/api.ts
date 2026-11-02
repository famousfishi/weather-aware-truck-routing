// The JSON contract with the Django API (mirrors backend/trips/dtos.py).

export type RiskLevel = 0 | 1 | 2 | 3 | 4;
export type SampleInterval = 10 | 25 | 50;

export interface LocationInput {
    query: string;
    lat?: number;
    lng?: number;
}

export interface TripPlanRequest {
    origin: LocationInput;
    destination: LocationInput;
    departure_time: string;
    load_weight_lb: number;
    sample_interval_miles: SampleInterval;
    weather?: WeatherBatch[];
}

// Browser-weather mode: a forecast download the server asks for, and what the browser sends back after fetching it.
export interface WeatherRequest {
    url: string;
    points: [number, number][];
}

export interface WeatherBatch {
    points: [number, number][];
    body: unknown;
}

export interface Place {
    label: string;
    lat: number;
    lng: number;
}

export interface Weather {
    wind_mph: number;
    rain_in_hr: number;
    snow_in_hr: number;
}

export interface Checkpoint {
    mile: number;
    lat: number;
    lng: number;
    eta: string;
    weather: Weather;
    risk_level: RiskLevel;
    risk_label: string;
    reasons: string[];
}

export interface RiskSegment {
    risk_level: RiskLevel;
    path: [number, number][];
}

export interface RouteSummary {
    low_miles: number;
    moderate_miles: number;
    high_miles: number;
    severe_miles: number;
    no_travel_miles: number;
    average_risk: number;
    worst_risk_level: RiskLevel;
}

export interface RouteOption {
    id: string;
    name: string;
    via: string[];
    distance_miles: number;
    duration_seconds: number;
    traffic_delay_seconds: number;
    departure_time: string;
    arrival_time: string;
    summary: RouteSummary;
    segments: RiskSegment[];
    checkpoints: Checkpoint[];
    rank: number;
    is_recommended: boolean;
}

export interface Recommendation {
    route_id: string;
    headline: string;
    reasons: string[];
    warnings: string[];
}

export interface HeatCell {
    lat: number;
    lng: number;
    risk_level: RiskLevel[];
    wind_mph: number[];
    rain_in_hr: number[];
    snow_in_hr: number[];
}

export interface Heatmap {
    start_time: string;
    hours: number;
    cell_size_deg: number;
    cells: HeatCell[];
}

export interface TripPlan {
    origin: Place;
    destination: Place;
    load_weight_lb: number;
    sample_interval_miles: SampleInterval;
    routes: RouteOption[];
    recommendation: Recommendation;
    heatmap: Heatmap;
}

export interface ServerStatus {
    status: string;
    demo_mode: boolean;
}