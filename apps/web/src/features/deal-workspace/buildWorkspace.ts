import type { Property } from "../../types/property";

import type { WorkspaceState } from "./types";

export function buildWorkspace(
    property: Property
): WorkspaceState {
    const researchComplete =
        property.research_completed ?? false;

    const buyersFound =
        (property.buyer_count ?? 0) > 0;

    const offerGenerated =
        property.offer_amount != null;

    if (!researchComplete) {
        return {
            stage: "research",

            title: "Run Property Research",

            description:
                "Research has not been completed yet.",

            progress: 25,

            researchComplete,

            buyersFound,

            offerGenerated,
        };
    }

    if (!buyersFound) {
        return {
            stage: "buyers",

            title: "Find Buyers",

            description:
                "Research is complete. Find potential wholesale buyers.",

            progress: 50,

            researchComplete,

            buyersFound,

            offerGenerated,
        };
    }

    if (!offerGenerated) {
        return {
            stage: "offer",

            title: "Generate Offer",

            description:
                "Buyer demand is known. Generate a recommended offer.",

            progress: 75,

            researchComplete,

            buyersFound,

            offerGenerated,
        };
    }

    return {
        stage: "complete",

        title: "Deal Ready",

        description:
            "Research, buyers, and offer have been completed.",

        progress: 100,

        researchComplete,

        buyersFound,

        offerGenerated,
    };
}