import type { Property } from "../../types/property";

export default function DealMetrics({ property }: { property: Property }) {
  const metrics = [
    ["Opportunity evaluation", property.opportunity_score ?? "Not evaluated"],
    ["Evidence confidence", property.confidence == null ? "Insufficient data" : `${property.confidence}%`],
    ["Parcel size", property.acres ? `${property.acres} ac` : "—"],
    ["Zoning", property.zoning ?? "Pending"],
  ];
  return <div className="deal-metrics">{metrics.map(([label, value]) => <div className="metric" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>;
}
