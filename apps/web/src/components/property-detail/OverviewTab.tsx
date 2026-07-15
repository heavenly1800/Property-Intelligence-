import BuyerMatchesCard from "./BuyerMatchesCard";
import type { Property } from "../../types/property";
import type { BuyerMatch } from "../../services/buyerService";
import type { ResearchResult } from "../../models/research";
import ResearchStatusCard from "./ResearchStatusCard";

type OverviewTabProps = {
  property: Property;
  buyers: BuyerMatch[];
  research: ResearchResult | null;
  researching: boolean;
  loadingBuyers: boolean;
  onRunResearch: () => void;
  onFindBuyers: () => void;
};

export default function OverviewTab({
  property,
  buyers,
  research,
  researching,
  loadingBuyers,
  onRunResearch,
  onFindBuyers,
}: OverviewTabProps) {
  return (
    <div className="overview-content">
      <div className="overview-actions">
        <button
          onClick={onRunResearch}
          disabled={researching}
          className="workspace-action primary"
        >
          {researching ? "Running Research..." : "Run Research"}
        </button>

        <button
          onClick={onFindBuyers}
          disabled={loadingBuyers}
          className="workspace-action success"
        >
          {loadingBuyers ? "Searching..." : "Find Buyers"}
        </button>

        <button className="workspace-action neutral">
          Generate Offer
        </button>
      </div>

      <ResearchStatusCard research={research} />

      <section className="command-card overview-section">
        <h2>Property Snapshot</h2>

        <div className="property-snapshot">
          <Info label="Address" value={property.address} />
          <Info label="APN" value={property.apn} />
          <Info label="County" value={property.county} />
          <Info label="State" value={property.state} />
          <Info label="Property Type" value={property.property_type} />
          <Info label="Acres" value={property.acres} />
          <Info label="Square Feet" value={property.square_feet} />
          <Info label="Zoning" value={property.zoning} />
        </div>
      </section>

      <section className="command-card overview-section">
        <h2>Census Intelligence</h2>

        <div className="property-snapshot">
          <Info label="Latitude" value={property.latitude} />
          <Info label="Longitude" value={property.longitude} />
          <Info label="Census Tract" value={property.census_tract} />
          <Info label="Block Group" value={property.block_group} />
        </div>
      </section>

      <section className="command-card overview-section">
        <h2>Flood Risk</h2>

        <div className="property-snapshot">
          <Info label="Flood Zone" value={property.flood_zone} />
          <Info
            label="Zone Detail"
            value={property.flood_zone_subtype}
          />
          <Info
            label="Special Flood Hazard Area"
            value={
              property.special_flood_hazard_area === undefined
                ? undefined
                : property.special_flood_hazard_area
                  ? "Yes"
                  : "No"
            }
          />
          <Info
            label="Risk Level"
            value={property.flood_risk_level}
          />
          <Info label="Source" value={property.flood_source} />
        </div>
      </section>

      <section className="command-card overview-section">
        <h2>Acquisition Summary</h2>

        <BuyerMatchesCard buyers={buyers} />

        <div className="acquisition-summary">
          <Info
            label="Opportunity Score"
            value={property.opportunity_score}
          />

          <Info
            label="Recommended Strategy"
            value={property.strategy}
          />

          <Info
            label="Next Action"
            value={property.next_action}
          />
        </div>
      </section>
    </div>
  );
}

type InfoProps = {
  label: string;
  value: string | number | undefined;
};

function Info({ label, value }: InfoProps) {
  return (
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="font-medium">{value ?? "—"}</p>
    </div>
  );
}
