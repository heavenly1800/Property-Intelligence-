import { useEffect, useState } from "react";

import DashboardLayout from "../components/layout/DashboardLayout";
import PropertyCard from "../components/property/PropertyCard";

import { getProperties } from "../services/propertyService";
import {
  buildDashboardStats,
  type DashboardStats,
} from "../services/dashboardService";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const properties = await getProperties();
        setStats(buildDashboardStats(properties));
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