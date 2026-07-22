import { useEffect, useState } from "react";

import DashboardLayout from "../components/layout/DashboardLayout";
import PropertyCard from "../components/property/PropertyCard";

import { getProperties } from "../services/propertyService";
import {
  buildDashboardStats,
  type DashboardStats,
} from "../services/dashboardService";
import { getCrmDashboard } from "../services/crmService";
import type { CrmDashboard } from "../types/crm";
import { getNotifications, getUnreadCount } from "../services/notificationService";
import type { Notification } from "../types/notification";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [crm,setCrm]=useState<CrmDashboard|null>(null);
  const [notifications,setNotifications]=useState<Notification[]>([]),[unread,setUnread]=useState(0);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [properties,crmData,notices,count] = await Promise.all([getProperties(),getCrmDashboard(),getNotifications({unread_only:true,include_dismissed:false}),getUnreadCount()]); setCrm(crmData);setNotifications(notices);setUnread(count.unread_count);
        setStats(buildDashboardStats(properties.map(p=>({...p,...crmData.property_summaries[p.property_id],workflow_stage:crmData.property_summaries[p.property_id]?.current_stage??p.workflow_stage}))));
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  return (
    <DashboardLayout>
      <h1>Good Evening, Heavenly 👋</h1>

      <h2>Today's Opportunities</h2>

      {loading && <p>Loading dashboard...</p>}

      {!loading && stats && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4,1fr)",
              gap: 20,
              marginTop: 30,
              marginBottom: 40,
            }}
          >
            <StatCard
              title="Properties"
              value={stats.totalProperties}
            />

            <StatCard
              title="Average Score"
              value={stats.averageOpportunityScore}
            />

            <StatCard
              title="Ready to Offer"
              value={stats.readyToOffer}
            />

            <StatCard
              title="Needs Research"
              value={stats.needsResearch}
            />
          </div>
          {crm&&<><h2>Acquisition workflow</h2><div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(140px,1fr))",gap:12,marginBottom:30}}><StatCard title="Overdue tasks" value={crm.overdue_tasks}/><StatCard title="Due today" value={crm.due_today}/><StatCard title="Due this week" value={crm.due_this_week}/><StatCard title="Under contract" value={crm.under_contract}/><StatCard title="Offers sent" value={crm.offers_sent}/><StatCard title="Follow-ups needed" value={crm.follow_ups_needed}/></div><p>{Object.entries(crm.leads_by_stage).map(([stage,count])=>`${stage.replaceAll("_"," ")}: ${count}`).join(" · ")}</p></>}

          <h2>Notification risks</h2><div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(140px,1fr))",gap:12}}><StatCard title="Unread" value={unread}/><StatCard title="Deadlines at risk" value={notifications.filter(n=>n.notification_type.includes("deadline")).length}/><StatCard title="Expiring offers" value={notifications.filter(n=>n.notification_type==="offer_expiring").length}/><StatCard title="Stale leads" value={notifications.filter(n=>n.notification_type==="stale_lead").length}/></div>{notifications.slice(0,5).map(n=><p key={n.notification_id}><strong>{n.severity.toUpperCase()}:</strong> {n.title} · {n.property_id}</p>)}

          <h2>Top Opportunities</h2>

          {stats.topProperties.length === 0 ? (
            <p>No properties available.</p>
          ) : (
            stats.topProperties.map((property) => (
              <PropertyCard
                key={property.property_id}
                property={property}
              />
            ))
          )}
        </>
      )}
    </DashboardLayout>
  );
}

type StatCardProps = {
  title: string;
  value: string | number;
};

function StatCard({
  title,
  value,
}: StatCardProps) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 20,
        background: "#fff",
      }}
    >
      <h3>{title}</h3>

      <h1>{value}</h1>
    </div>
  );
}
