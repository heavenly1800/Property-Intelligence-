import { api } from "../lib/api";
import { endpoints } from "../lib/endpoints";

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

    purchase_count: number | null;

    confidence: number | null;

    score?: BuyerScore;

    strengths?: string[];

    concerns?: string[];

    recommendation?: string;
}

export interface BuyerMatchResult {
    buyers: BuyerMatch[];

    recommended_buyer: BuyerMatch | null;

    average_confidence: number | null;

    market_demand: string;

    status: "verified_buyers_found" | "no_verified_buyers";

    message: string;

    generated_at: string;
}

export function getBuyers(
    propertyId: string
) {
    return api.get<BuyerMatchResult>(
        endpoints.buyers(propertyId)
    );
}
