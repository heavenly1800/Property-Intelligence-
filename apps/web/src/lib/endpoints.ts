export const endpoints = {
    properties: "/properties",

    property: (id: string) =>
        `/properties/${id}`,

    financials: (id: string) =>
        `/properties/${id}/financials`,

    research: (id: string) =>
        `/research/${id}`,

    buyers: (id: string) =>
        `/buyers/${id}`,

    decision: (id: string) =>
        `/decision/${id}`,

    offer: (id: string) =>
        `/offer/${id}`,
};
