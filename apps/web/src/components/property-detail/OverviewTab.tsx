import BuyerMatchesCard from "./BuyerMatchesCard";
import type { Property } from "../../types/property";
import type { BuyerMatch } from "../../services/buyerService";
import type { ResearchResult } from "../../models/research";
import ResearchStatusCard from "./ResearchStatusCard";
import FinancialIntelligenceCard from "./FinancialIntelligenceCard";
import PropertyMediaGallery from "./PropertyMediaGallery";
import ListingIntelligenceCard from "./ListingIntelligenceCard";
import AIConditionAnalysisCard from "./AIConditionAnalysisCard";
import ComparablesSection from "./ComparablesSection";
import DealStrategySection from "./DealStrategySection";

type OverviewTabProps = {
  property: Property;
  buyers: BuyerMatch[];
  research: ResearchResult | null;
  researching: boolean;
  loadingBuyers: boolean;
  onRunResearch: () => void;
  onFindBuyers: () => void;
  onRefreshProperty: () => Promise<void>;
  onGenerateOffer: () => void;
};

export default function OverviewTab({
  property,
  buyers,
  research,
  researching,
  loadingBuyers,
  onRunResearch,
  onFindBuyers,
  onRefreshProperty,
  onGenerateOffer,
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

        <button className="workspace-action neutral" onClick={onGenerateOffer}>
          Generate Offer
        </button>
      </div>

      <ResearchStatusCard research={research} />

      <FinancialIntelligenceCard property={property} onSaved={onRefreshProperty}>
        <AIConditionAnalysisCard propertyId={property.property_id} />
      </FinancialIntelligenceCard>
      <ComparablesSection propertyId={property.property_id} />
      <DealStrategySection propertyId={property.property_id} />
      <PropertyMediaGallery propertyId={property.property_id} />
      <ListingIntelligenceCard property={property} onSaved={onRefreshProperty} />

      <section className="command-card overview-section">
        <h2>Research Quality</h2>

        <div className="property-snapshot">
          <Info label="Score" value={property.research_quality_score} />
          <Info label="Overall Risk" value={property.research_risk_level} />
          <Info label="Parcel Certainty" value={property.parcel_certainty} />
          <Info
            label="Assessment Coverage"
            value={property.assessment_coverage}
          />
          <Info
            label="Utility Confidence"
            value={property.utility_confidence}
          />
          <Info
            label="Recommended Next Step"
            value={property.recommended_research_action}
          />
        </div>

        <div className="mt-4">
          <p className="text-sm text-gray-500">Missing Research Items</p>
          <p className="font-medium">
            {property.missing_research_items?.join(" · ") ?? "—"}
          </p>
        </div>
      </section>

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
        <h2>Parcel Intelligence</h2>

        <div className="property-snapshot">
          <Info label="APN" value={property.apn} />
          <Info label="Parcel Acres" value={property.parcel_acres} />
          <Info label="Zoning" value={property.zoning} />
          <Info label="Jurisdiction" value={property.jurisdiction} />
          <Info label="Land Use" value={property.land_use} />
          <Info label="Source" value={property.parcel_source} />
        </div>
      </section>

      <section className="command-card overview-section">
        <h2>Ownership &amp; Assessment</h2>

        <div className="property-snapshot">
          <Info label="Owner" value={property.owner_name} />
          <Info
            label="Mailing Address"
            value={property.owner_mailing_address}
          />
          <Info
            label="Assessed Land Value"
            value={property.assessed_land_value}
          />
          <Info
            label="Assessed Improvement Value"
            value={property.assessed_improvement_value}
          />
          <Info
            label="Assessed Total Value"
            value={property.assessed_total_value}
          />
          <Info label="Tax Year" value={property.tax_year} />
          <Info label="Tax Status" value={property.tax_status} />
          <Info
            label="Last Transfer Date"
            value={property.last_transfer_date}
          />
          <Info
            label="Last Transfer Price"
            value={property.last_transfer_price}
          />
          <Info label="Source" value={property.assessor_source} />
        </div>
      </section>

      <section className="command-card overview-section">
        <h2>Utilities</h2>

        <div className="property-snapshot">
          <Info label="Electric Provider" value={property.electric_provider} />
          <Info
            label="Electric Evidence"
            value={property.electric_service_evidence}
          />
          <Info label="Gas Provider" value={property.gas_provider} />
          <Info label="Gas Evidence" value={property.gas_service_evidence} />
          <Info label="Water Provider" value={property.water_provider} />
          <Info
            label="Water Evidence"
            value={property.water_service_evidence}
          />
          <Info label="Sewer Provider" value={property.sewer_provider} />
          <Info
            label="Sewer Evidence"
            value={property.sewer_service_evidence}
          />
          <Info label="Broadband" value={property.broadband_summary} />
          <Info
            label="Broadband Evidence"
            value={property.broadband_evidence}
          />
          <Info label="Sources" value={property.utilities_source} />
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
