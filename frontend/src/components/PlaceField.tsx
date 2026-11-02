import { Autocomplete, TextField } from '@mui/material';
import { useEffect, useState } from 'react';
import { tripApi } from '../api/tripApi';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import type { LocationInput, Place } from '../types/api';

interface Props {
    label: string;
    value: LocationInput;
    onChange: (value: LocationInput) => void;
    disabled?: boolean;
}

// Search-as-you-type place box. Picking a suggestion stores its coordinates, so the server skips geocoding.
export function PlaceField({ label, value, onChange, disabled }: Props) {
    const [options, setOptions] = useState<Place[]>([]);
    const [loading, setLoading] = useState(false);
    const query = useDebouncedValue(value.query, 300);
    const picked = value.lat !== undefined;

    useEffect(() => {
        if (picked || query.trim().length < 3) {
            setOptions([]);
            setLoading(false);
            return;
        }
        const controller = new AbortController();
        setLoading(true);
        tripApi
            .suggestPlaces(query, controller.signal)
            .then(setOptions)
            .catch(() => !controller.signal.aborted && setOptions([]))
            .finally(() => !controller.signal.aborted && setLoading(false));
        return () => controller.abort();
    }, [query, picked]);

    return (
        <Autocomplete<Place, false, false, true>
            freeSolo
            options={options}
            filterOptions={(items) => items}
            getOptionLabel={(option) => (typeof option === 'string' ? option : option.label)}
            getOptionKey={(option) => (typeof option === 'string' ? option : `${option.label}|${option.lat}|${option.lng}`)}
            inputValue={value.query}
            onInputChange={(_, text, reason) => {
                if (reason === 'input' || reason === 'clear') onChange({ query: text });
            }}
            onChange={(_, selected) => {
                if (selected && typeof selected !== 'string') onChange({ query: selected.label, lat: selected.lat, lng: selected.lng });
            }}
            loading={loading}
            disabled={disabled}
            renderInput={(params) => <TextField {...params} label={label} placeholder="City, address or depot" required />}
        />
    );
}