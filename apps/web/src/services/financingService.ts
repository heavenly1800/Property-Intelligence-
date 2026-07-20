import {api} from "../lib/api";
import type {FinancingAnalysis,FinancingScenario,FinancingScenarioInput} from "../types/financing";
const base=(id:string)=>`/properties/${id}`;
export const listFinancingScenarios=(id:string)=>api.get<FinancingScenario[]>(`${base(id)}/financing-scenarios`);
export const createFinancingScenario=(id:string,value:FinancingScenarioInput)=>api.post<FinancingScenario>(`${base(id)}/financing-scenarios`,value);
export const updateFinancingScenario=(id:string,scenarioId:string,value:Partial<FinancingScenarioInput>)=>api.patch<FinancingScenario>(`${base(id)}/financing-scenarios/${scenarioId}`,value);
export const analyzeFinancingScenario=(id:string,scenarioId:string)=>api.post<FinancingAnalysis>(`${base(id)}/financing-scenarios/${scenarioId}/analyze`,{});
export const getFinancingAnalysis=(id:string)=>api.get<FinancingAnalysis>(`${base(id)}/financing-analysis`);
export const getFinancingHistory=(id:string)=>api.get<FinancingAnalysis[]>(`${base(id)}/financing-analysis/history`);
