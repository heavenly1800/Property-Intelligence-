import DashboardLayout from "../components/layout/DashboardLayout";
import { useParams } from "react-router-dom";

export default function PropertyDetail() {
  const { id } = useParams();

  return (
    <DashboardLayout>
      <h1>Property Detail</h1>

      <h2>{id}</h2>

      <hr />

      <h3>Opportunity Score</h3>

      <h1>Coming Soon</h1>

      <h3>Recommended Strategy</h3>

      <p>Coming Soon</p>

      <h3>AI Summary</h3>

      <p>Coming Soon</p>

      <h3>Timeline</h3>

      <p>Coming Soon</p>
    </DashboardLayout>
  );
}