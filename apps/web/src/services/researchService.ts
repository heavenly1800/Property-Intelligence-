import { api } from "../lib/api";
import { endpoints } from "../lib/endpoints";
import type { ResearchResult } from "../models/research";

export function runResearch(
    propertyId: string
) {
    return api.post<ResearchResult>(
        endpoints.research(propertyId)
    );
}
