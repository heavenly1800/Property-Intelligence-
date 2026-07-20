import type { Property } from "../../types/property";

type PropertyWorkspaceHeaderProps = { property: Property };

export default function PropertyWorkspaceHeader({ property }: PropertyWorkspaceHeaderProps) {
  const stage = (property.workflow_stage ?? "NEW_LEAD").replaceAll("_", " ");
  return (
    <header className="workspace-header">
      <div>
        <p className="eyebrow">Acquisition command center</p>
        <h1>{property.address}</h1>
        <div className="property-meta">
          <span>{property.county ?? "County unavailable"}</span>
          <span>APN {property.apn ?? "—"}</span>
          <span>{property.property_type ?? "Property type unavailable"}</span>
          <span>{property.acres ?? "—"} acres</span>
        </div>
      </div>
      <div className="header-badges">
        <span className="score-badge">Score {property.opportunity_score ?? "—"}</span>
        <span className="stage-badge">{stage}</span>
      </div>
    </header>
  );
}
