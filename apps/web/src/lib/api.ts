const API_BASE_URL =
    import.meta.env.VITE_API_URL ??
    "http://127.0.0.1:8000";

export class ApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.status = status;
    }
}

async function request<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            headers: {
                "Content-Type": "application/json",
                ...(options?.headers ?? {}),
            },
            ...options,
        }
    );

    if (!response.ok) {
        const body = await response.json().catch(() => null) as { detail?: string } | null;
        throw new ApiError(
            body?.detail ?? response.statusText,
            response.status
        );
    }

    if (response.status === 204) {
        return undefined as T;
    }

    return response.json();
}

export const api = {
    get: <T>(endpoint: string) =>
        request<T>(endpoint),

    post: <T>(
        endpoint: string,
        body?: unknown
    ) =>
        request<T>(endpoint, {
            method: "POST",
            body: JSON.stringify(body),
        }),

    put: <T>(
        endpoint: string,
        body?: unknown
    ) =>
        request<T>(endpoint, {
            method: "PUT",
            body: JSON.stringify(body),
        }),

    patch: <T>(endpoint: string, body?: unknown) =>
        request<T>(endpoint, { method: "PATCH", body: JSON.stringify(body) }),

    delete: <T>(endpoint: string) =>
        request<T>(endpoint, {
            method: "DELETE",
        }),
};
