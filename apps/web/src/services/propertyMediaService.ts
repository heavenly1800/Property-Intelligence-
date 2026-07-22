import type { AnalyzeAllResult, PropertyConditionSummary, PropertyMedia, PropertyMediaAnalysis, PropertyMediaUpdate } from "../types/propertyMedia";

const baseUrl = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, init);
  if (!response.ok) throw new Error(await response.text() || response.statusText);
  return response.status === 204 ? undefined as T : response.json();
}

export const listPropertyMedia = (propertyId: string) => request<PropertyMedia[]>(`/properties/${propertyId}/media`);
export const uploadPropertyMedia = (propertyId: string, file: File) => { const form = new FormData(); form.append("file", file); return request<PropertyMedia>(`/properties/${propertyId}/media`, { method: "POST", body: form }); };
export const updatePropertyMedia = (propertyId: string, mediaId: string, data: Partial<PropertyMediaUpdate>) => request<PropertyMedia>(`/properties/${propertyId}/media/${mediaId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const deletePropertyMedia = (propertyId: string, mediaId: string) => request<void>(`/properties/${propertyId}/media/${mediaId}`, { method: "DELETE" });
export const setPrimaryPropertyMedia = (propertyId: string, mediaId: string) => request<PropertyMedia>(`/properties/${propertyId}/media/${mediaId}/primary`, { method: "POST" });
export const analyzePropertyMedia = (propertyId: string, mediaId: string, reanalyze = false) => request<PropertyMediaAnalysis>(`/properties/${propertyId}/media/${mediaId}/analyze?reanalyze=${reanalyze}`, { method: "POST" });
export const analyzeAllPropertyMedia = (propertyId: string, reanalyze = false) => request<AnalyzeAllResult>(`/properties/${propertyId}/media/analyze-all?reanalyze=${reanalyze}`, { method: "POST" });
export const getPropertyMediaAnalysis = (propertyId: string, mediaId: string) => request<PropertyMediaAnalysis>(`/properties/${propertyId}/media/${mediaId}/analysis`);
export const getPropertyConditionSummary = (propertyId: string) => request<PropertyConditionSummary | null>(`/properties/${propertyId}/media/analysis-summary`);
