import { api } from "../lib/api";
import type { StrategyAnalysis } from "../types/strategyAnalysis";

const base = (propertyId: string) => `/properties/${propertyId}/strategy-analysis`;
export const getStrategyAnalysis = (propertyId: string) => api.get<StrategyAnalysis>(base(propertyId));
export const createStrategyAnalysis = (propertyId: string) => api.post<StrategyAnalysis>(base(propertyId));
export const recalculateStrategyAnalysis = (propertyId: string) => api.post<StrategyAnalysis>(`${base(propertyId)}/recalculate`);
