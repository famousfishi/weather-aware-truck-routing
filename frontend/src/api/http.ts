export class ApiError extends Error {
    status: number;
    body: unknown;

    constructor(message: string, status = 0, body: unknown = null) {
        super(message);
        this.status = status;
        this.body = body;
    }
}

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
        throw new ApiError(body?.detail ?? `The server returned an error (${response.status}).`, response.status, body);
    }
    return body as T;
}