import { api } from "../lib/api";
import { endpoints } from "../lib/endpoints";
import type { Property } from "../types/property";

export async function getProperties(): Promise<Property[]> {
    return api.get<Property[]>(endpoints.properties);
}

export async function getProperty(
    id: string
): Promise<Property> {
    return api.get<Property>(endpoints.property(id));
}

export async function createProperty(
    property: Partial<Property>
): Promise<Property> {
    return api.post<Property>(
        endpoints.properties,
        property
    );
}

export async function updateProperty(
    id: string,
    property: Partial<Property>
): Promise<Property> {
    return api.put<Property>(
        endpoints.property(id),
        property
    );
}

export async function deleteProperty(
    id: string
): Promise<void> {
    return api.delete<void>(
        endpoints.property(id)
    );
}

export async function updateFinancials(
    id: string,
    property: Partial<Property>
): Promise<Property> {
    return api.put<Property>(endpoints.financials(id), property);
}
