import { api } from "../lib/api";
import type { ComparableAnalysis, ComparableInput, PropertyComparable } from "../types/comparable";

const base = (propertyId: string) => `/properties/${propertyId}/comparables`;
export const listComparables = (propertyId: string) => api.get<PropertyComparable[]>(base(propertyId));
export const createComparable = (propertyId: string, value: ComparableInput) => api.post<PropertyComparable>(base(propertyId), value);
export const updateComparable = (propertyId: string, comparableId: string, value: Partial<ComparableInput>) => api.patch<PropertyComparable>(`${base(propertyId)}/${comparableId}`, value);
export const deleteComparable = (propertyId: string, comparableId: string) => api.delete<void>(`${base(propertyId)}/${comparableId}`);
export const analyzeComparables = (propertyId: string) => api.post<ComparableAnalysis>(`${base(propertyId)}/analyze`);
export const getComparableAnalysis = (propertyId: string) => api.get<ComparableAnalysis>(`${base(propertyId)}/analysis`);
