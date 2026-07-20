import { api } from "../lib/api";
import type { OfferAnalysis, OfferStrategy } from "../types/offerAnalysis";
const base=(propertyId:string)=>`/properties/${propertyId}`;
export const getOfferAnalysis=(propertyId:string)=>api.get<OfferAnalysis>(`${base(propertyId)}/offer-analysis`);
export const calculateOffer=(propertyId:string,selected_strategy:OfferStrategy,allow_over_asking_offer=false)=>api.post<OfferAnalysis>(`${base(propertyId)}/offer-analysis`,{selected_strategy,allow_over_asking_offer});
export const recalculateOffer=(propertyId:string,selected_strategy:OfferStrategy,allow_over_asking_offer=false)=>api.post<OfferAnalysis>(`${base(propertyId)}/offer-analysis/recalculate`,{selected_strategy,allow_over_asking_offer});
export const saveManualOffer=(propertyId:string,target_offer:number,target_margin?:number,notes?:string)=>api.post<OfferAnalysis>(`${base(propertyId)}/offer-analysis/manual`,{target_offer,target_margin,notes});
export const getOfferHistory=(propertyId:string)=>api.get<OfferAnalysis[]>(`${base(propertyId)}/offer-history`);
