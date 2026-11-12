import type { Property } from "../types/property";

export interface DashboardStats {
  totalProperties: number;
  averageOpportunityScore: number | null;
  evaluatedProperties: number;
  needsResearch: number;
  topProperties: Property[];
}

export function buildDashboardStats(
  properties: Property[]
): DashboardStats {
  const totalProperties = properties.length;

  const scoredProperties = properties.filter(
    (property) =>
      property.opportunity_score !== undefined &&
      property.opportunity_score !== null
  );

  const averageOpportunityScore =
    scoredProperties.length === 0
      ? null
      : Math.round(
          scoredProperties.reduce(
            (sum, property) =>
              sum + (property.opportunity_score ?? 0),
            0
          ) / scoredProperties.length
        );

  const needsResearch = properties.filter(
    (property) =>
      property.opportunity_score === undefined ||
      property.opportunity_score === null
  ).length;

  const topProperties = properties.slice(0, 5);

  return {
    totalProperties,
    averageOpportunityScore,
    evaluatedProperties: scoredProperties.length,
    needsResearch,
    topProperties,
  };
}
