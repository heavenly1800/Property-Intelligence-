import { api } from "../lib/api";
import { endpoints } from "../lib/endpoints";

export interface ResearchResult {
    provider_status: Record<string, string>;
    completed: boolean;
}

export function runResearch(
    propertyId: string
) {
    return api.post<ResearchResult>(
        endpoints.research(propertyId)
    );
}