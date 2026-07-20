import { useEffect, useState } from "react";

import DashboardLayout from "../components/layout/DashboardLayout";
import PropertyForm from "../components/property/PropertyForm";
import PropertyList from "../components/property/PropertyList";
import PropertySearch from "../components/property/PropertySearch";

import { getProperties } from "../services/propertyService";
import type { Property } from "../types/property";
import type { WorkflowStage } from "../types/property";
import { getCrmDashboard } from "../services/crmService";

export default function Properties() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [search, setSearch] = useState("");
  const [stage,setStage]=useState<WorkflowStage|"ALL">("ALL"),[overdue,setOverdue]=useState(false),[assigned,setAssigned]=useState(""),[showArchived,setShowArchived]=useState(false);

  useEffect(() => {
    Promise.all([getProperties(),getCrmDashboard()]).then(([items,crm])=>setProperties(items.map(p=>({...p,...crm.property_summaries[p.property_id],workflow_stage:crm.property_summaries[p.property_id]?.current_stage??p.workflow_stage}))));
  }, []);

  const filteredProperties = properties.filter((property) =>
    `${property.address} ${property.city} ${property.property_type}`
      .toLowerCase()
      .includes(search.toLowerCase())
  ).filter(p=>stage==="ALL"||p.workflow_stage===stage).filter(p=>!overdue||p.has_overdue).filter(p=>!assigned||p.crm_assigned_to?.toLowerCase().includes(assigned.toLowerCase())).filter(p=>showArchived||p.workflow_stage!=="ARCHIVED");

  return (
    <DashboardLayout>
      <div
        style={{
          maxWidth: 1200,
          margin: "auto",
        }}
      >
        <h1>Properties</h1>

        <PropertySearch
          value={search}
          onChange={setSearch}
        />
        <div style={{display:"flex",gap:10,flexWrap:"wrap",margin:"12px 0"}}><select value={stage} onChange={e=>setStage(e.target.value as WorkflowStage|"ALL")}><option value="ALL">All stages</option>{["NEW_LEAD","RESEARCH","READY_TO_OFFER","OFFER_SENT","NEGOTIATING","UNDER_CONTRACT","MARKETING","SOLD","ARCHIVED"].map(x=><option key={x}>{x}</option>)}</select><label><input type="checkbox" checked={overdue} onChange={e=>setOverdue(e.target.checked)}/> Overdue follow-up</label><input placeholder="Assigned user" value={assigned} onChange={e=>setAssigned(e.target.value)}/><label><input type="checkbox" checked={showArchived} onChange={e=>setShowArchived(e.target.checked)}/> Include archived</label></div>

        <PropertyForm />

        <PropertyList
          properties={filteredProperties}
        />
      </div>
    </DashboardLayout>
  );
}
