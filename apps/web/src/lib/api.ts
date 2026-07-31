import { publicConfig } from "./config";

const API_BASE_URL = publicConfig?.apiUrl ?? "";

export class ApiError extends Error {
    status: number;
    requestId?: string;

    constructor(message: string, status: number, requestId?: string) {
        super(message);
        this.status = status;
        this.requestId = requestId;
    }
}

async function request<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    const session=getSession();const organizationId=getSelectedOrganization();
    let response: Response;
    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                "Content-Type": "application/json",
                ...(session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {}),
                ...(organizationId ? { "X-Organization-ID": organizationId } : {}),
                ...(options?.headers ?? {}),
            },
            ...options,
        });
    } catch {
        throw new ApiError("The API is unreachable. Check your connection and try again.", 0);
    }

    if (!response.ok) {
        const body = await response.json().catch(() => null) as { detail?: string; message?: string; request_id?: string } | null;
        if(response.status===401){clearAuth();if(location.pathname!=="/sign-in")location.assign("/sign-in");}
        const requestId=body?.request_id??response.headers.get("X-Request-ID")??undefined;
        const fallback=response.status===403?"You do not have permission for this action.":response.status===429?`Too many requests. Try again in ${response.headers.get("Retry-After")??"a few"} seconds.`:response.statusText||"Network request failed.";
        throw new ApiError(
            `${body?.message??body?.detail??fallback}${requestId&&response.status>=500?` Request ID: ${requestId}`:""}`,
            response.status,
            requestId
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
import { clearAuth, getSelectedOrganization, getSession } from "../services/authStorage";
