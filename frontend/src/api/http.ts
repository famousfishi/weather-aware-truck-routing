export class ApiError extends Error { }

// Every API error from Django comes back as { "detail": "..." }.
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
    let response: Response;
    try {
        response = await fetch(`/api${path}`, {
            ...init,
            headers: { 'Content-Type': 'application/json', ...init?.headers },
        });
    } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') throw error;
        throw new ApiError('Could not reach the server. Check your connection and try again.');
    }

    const body = await response.json().catch(() => null);
    if (!response.ok) {
        throw new ApiError(body?.detail ?? `The server returned an error (${response.status}).`);
    }
    return body as T;
}