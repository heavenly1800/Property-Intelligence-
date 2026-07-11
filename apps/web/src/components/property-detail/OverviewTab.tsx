import { useState } from "react";

import BuyerMatchesCard from "./BuyerMatchesCard";

import {
  getBuyers,
  type Buyer,
} from "../../services/buyerService";

import type { Property } from "../../types/property";
import {
  runResearch,
  type ResearchResult,
} from "../../services/researchService";

type OverviewTabProps = {
  property: Property;
};

export default function OverviewTab({
  property,
}: OverviewTabProps) {
  const [researching, setResearching] = useState(false);
  const [research, setResearch] =
    useState<ResearchResult | null>(null);

  const [buyers, setBuyers] = useState<Buyer[]>([]);
  const [loadingBuyers, setLoadingBuyers] = useState(false);

  async function handleRunResearch() {
    setResearching(true);

    try {
      const result = await runResearch(property.property_id);

      setResearch(result);

      alert("Research completed successfully.");

      window.location.reload();
    } catch (error) {
      console.error(error);
      alert("Unable to run research.");
    } finally {
      setResearching(false);
    }
  }

  async function handleFindBuyers() {
    setLoadingBuyers(true);

    try {
      const result = await getBuyers(property.property_id);

      setBuyers(result.buyers);
    } catch (error) {
      console.error(error);
      alert("Unable to find buyers.");
    } finally {
      setLoadingBuyers(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-end gap-3">
        <button
          onClick={handleRunResearch}
          disabled={researching}
          className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {researching ? "Running Research..." : "Run Research"}
        </button>

        <button
          onClick={handleFindBuyers}
          disabled={loadingBuyers}
          className="rounded bg-green-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {loadingBuyers ? "Searching..." : "Find Buyers"}
        </button>

        <button className="rounded bg-gray-800 px-4 py-2 text-white">
          Generate Offer
        </button>
      </div>

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-6 text-xl font-semibold">
          Research Status
        </h2>

        <ResearchRow
          name="Census Geocoder"
          status={
            research?.provider_status?.CensusProvider ??
            "Not Run"
          }
        />

        <ResearchRow
          name="FEMA Flood"
          status="Pending"
        />

        <ResearchRow
          name="County GIS"
          status="Pending"
        />

        <ResearchRow
          name="Tax Assessor"
          status="Pending"
        />

        <ResearchRow
          name="Utilities"
          status="Pending"
        />

        <ResearchRow
          name="Buyer Discovery"
          status="Pending"
        />
      </section>

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-6 text-xl font-semibold">
          Property Snapshot
        </h2>

        <div className="grid gap-6 md:grid-cols-2">
          <Info label="Address" value={property.address} />
          <Info label="APN" value={property.apn} />
          <Info label="County" value={property.county} />
          <Info label="State" value={property.state} />
          <Info
            label="Property Type"
            value={property.property_type}
          />
          <Info label="Acres" value={property.acres} />
          <Info
            label="Square Feet"
            value={property.square_feet}
          />
          <Info label="Zoning" value={property.zoning} />
        </div>
      </section>

      <section className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-6 text-xl font-semibold">
          Acquisition Summary
        </h2>

        <BuyerMatchesCard buyers={buyers} />

        <div className="grid gap-6 md:grid-cols-3">
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
  value: unknown;
};

function Info({ label, value }: InfoProps) {
  return (
    <div>
      <p className="text-sm text-gray-500">
        {label}
      </p>

      <p className="font-medium">
        {value ?? "—"}
      </p>
    </div>
  );
}

type ResearchRowProps = {
  name: string;
  status: string;
};

function ResearchRow({
  name,
  status,
}: ResearchRowProps) {
  return (
    <div className="flex items-center justify-between border-b py-2 last:border-b-0">
      <span>{name}</span>

      <span className="font-medium">
        {status}
      </span>
    </div>
  );
}