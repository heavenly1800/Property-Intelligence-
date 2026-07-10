import { api } from "../lib/api";
import { Property } from "../types/property";

export function getProperties() {
  return api<Property[]>("/properties");
}

export function getProperty(id: string) {
  return api<Property>(`/properties/${id}`);
}

export function createProperty(property: Property) {
  return api<Property>("/properties", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(property),
  });
}