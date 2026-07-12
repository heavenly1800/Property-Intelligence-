import { api } from "../lib/api";
import { endpoints } from "../lib/endpoints";

export interface Buyer {
    buyer_name: string;
    purchase_count: number;
    confidence: number;
    reasons: string[];
}

export interface BuyerResponse {
    buyers: Buyer[];
}

export function getBuyers(
    propertyId: string
) {
    return api.get<BuyerResponse>(
        endpoints.buyers(propertyId)
    );
}
