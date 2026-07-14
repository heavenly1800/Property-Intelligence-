import { api } from "../lib/api";
import { endpoints } from "../lib/endpoints";

/**
 * Legacy buyer returned from the backend.
 * This stays here for compatibility while we migrate
 * to the Buyer Intelligence model.
 */
export interface Buyer {
    buyer_name: string;
    purchase_count: number;
    confidence: number;
    reasons: string[];
}

/**
 * Detailed score returned by the Buyer Intelligence Engine.
 * These fields are optional for now so the UI remains compatible
 * with both legacy and new backend responses.
 */
export interface BuyerScore {
    overall_score: number;

    distance_score?: number;
    county_score?: number;
    purchase_frequency_score?: number;
    recency_score?: number;
    property_type_score?: number;
    acreage_score?: number;
}

export interface BuyerMatch {
    buyer_name: string;

    purchase_count: number;

    confidence: number;

    score?: BuyerScore;

    strengths?: string[];

    concerns?: string[];

    recommendation?: string;
}

export interface BuyerMatchResult {
    buyers: BuyerMatch[];

    recommended_buyer?: BuyerMatch;

    average_confidence?: number;

    market_demand?: string;
}

/**
 * Current API contract.
 *
 * We intentionally keep this compatible with the existing backend.
 * When the backend begins returning BuyerMatchResult directly,
 * this interface can be simplified without affecting the rest of
 * the application.
 */
export interface BuyerResponse {
    buyers: BuyerMatch[];
}

export function getBuyers(
    propertyId: string
) {
    return api.get<BuyerResponse>(
        endpoints.buyers(propertyId)
    );
}
