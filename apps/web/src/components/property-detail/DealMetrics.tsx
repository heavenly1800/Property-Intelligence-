import type { Property } from "../../types/property";

export default function DealMetrics({ property }: { property: Property }) {
  const metrics = [
    ["Opportunity score", property.opportunity_score ?? "—"],
    ["Decision confidence", property.confidence ? `${property.confidence}%` : "—"],
    ["Parcel size", property.acres ? `${property.acres} ac` : "—"],
    ["Zoning", property.zoning ?? "Pending"],
  ];
  return <div className="deal-metrics">{metrics.map(([label, value]) => <div className="metric" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>;
}
