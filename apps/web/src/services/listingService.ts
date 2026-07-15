import { api } from "../lib/api";
import { endpoints } from "../lib/endpoints";
import type { Property } from "../types/property";

export const analyzeListing = (propertyId: string, listing_raw_text: string) => api.post<Property>(endpoints.listingAnalysis(propertyId), { listing_raw_text });
