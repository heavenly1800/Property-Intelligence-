import DashboardLayout from "../components/layout/DashboardLayout";
import PageHeader from "../components/ui/PageHeader";
import PropertyIntakeForm from "../components/property/PropertyIntakeForm";
import { Link } from "react-router-dom";

export default function Intake() {
  return (
    <DashboardLayout>
      <PageHeader
        title="Property Intake"
        subtitle="Paste an address, APN, or property link to begin analysis."
      />

      <PropertyIntakeForm />
      <div style={{ marginTop: 20 }}>
        <Link to="/share">Share Listing</Link>
        <p>Paste listing text, save its source URL, and optionally attach photos.</p>
      </div>
    </DashboardLayout>
  );
}
