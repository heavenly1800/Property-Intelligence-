import { api } from "../lib/api";
import { endpoints } from "../lib/endpoints";

export interface Buyer {
    id: string;
    name: string;
    city: string;
    state: string;
    last_purchase_price?: number;
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