import { useState } from "react";

import { useProperty } from "../../context/useProperty";
import { useWorkflow } from "../../features/workflow/useWorkflow";
import BuyerMatchesCard from "./BuyerMatchesCard";
import DealMetrics from "./DealMetrics";
import DecisionPanel from "./DecisionPanel";
import OverviewTab from "./OverviewTab";
import PropertyWorkspaceHeader from "./PropertyWorkspaceHeader";
import ResearchStatusCard from "./ResearchStatusCard";
import OfferCalculatorSection from "./OfferCalculatorSection";
import FinancingSection from "./FinancingSection";
import "./PropertyDetailPage.css";

type Tab = "Overview" | "Research" | "Buyers" | "Offers" | "Financing" | "Timeline" | "Notes" | "Documents" | "AI";
const tabs: Tab[] = ["Overview", "Research", "Buyers", "Offers", "Financing", "Timeline", "Notes", "Documents", "AI"];

export default function PropertyDetailPage() {
  const { property, loading, refresh } = useProperty();
  const [tab, setTab] = useState<Tab>("Overview");
  const { workflow, decision, research, buyers, isExecuting, executeNextAction, runResearch, findBuyers } = useWorkflow({ property, refreshProperty: refresh });

  if (loading) return <div className="workspace-loading">Loading property workspace…</div>;
  if (!property) return <div className="workspace-loading">Property not found.</div>;
  const currentProperty = property;

  function renderTab() {
    if (tab === "Overview") return <OverviewTab property={currentProperty} buyers={buyers} research={research} researching={isExecuting} loadingBuyers={isExecuting} onRunResearch={runResearch} onFindBuyers={findBuyers} onRefreshProperty={refresh} onGenerateOffer={() => setTab("Offers")} />;
    if (tab === "Research") return <ResearchStatusCard research={research} />;
    if (tab === "Buyers") return <BuyerMatchesCard buyers={buyers} />;
    if (tab === "Offers") return <OfferCalculatorSection propertyId={currentProperty.property_id} />;
    if (tab === "Financing") return <FinancingSection propertyId={currentProperty.property_id} />;
    return <section className="command-card empty-workspace"><p className="eyebrow">{tab}</p><h2>{tab} workspace</h2><p>This workspace is ready for your team’s {tab.toLowerCase()} activity.</p></section>;
  }

  return (
    <main className="acquisition-workspace">
      <PropertyWorkspaceHeader property={currentProperty} />
      <div className="workspace-grid">
        <div className="workspace-primary">
          {workflow && decision && <DecisionPanel decision={decision} workflow={workflow} loading={isExecuting} onAction={executeNextAction} />}
          <DealMetrics property={currentProperty} />
          <section className="tabbed-workspace">
            <div className="tab-list" role="tablist">{tabs.map((name) => <button key={name} role="tab" aria-selected={tab === name} className={tab === name ? "active" : ""} onClick={() => setTab(name)}>{name}</button>)}</div>
            <div className="tab-content">{renderTab()}</div>
          </section>
        </div>
        <aside className="workspace-sidebar">
          <section className="command-card ai-summary"><p className="eyebrow">AI brief</p><h2>Acquisition Summary</h2><p>{decision?.reasons[0] ?? "Run the decision engine to generate an acquisition brief for this property."}</p><p className="next-action">Next: {decision?.nextAction ?? property.next_action ?? "Review property details"}</p></section>
          <section className="command-card facts-card"><p className="eyebrow">At a glance</p><h2>Quick Property Facts</h2><dl><div><dt>Owner</dt><dd>{property.owner_name ?? "Pending research"}</dd></div><div><dt>Size</dt><dd>{property.square_feet ? `${property.square_feet.toLocaleString()} sq ft` : "—"}</dd></div><div><dt>Zoning</dt><dd>{property.zoning ?? "Pending research"}</dd></div><div><dt>Strategy</dt><dd>{property.strategy ?? "Under review"}</dd></div></dl></section>
          <ResearchStatusCard research={research} compact />
        </aside>
      </div>
    </main>
  );
}
