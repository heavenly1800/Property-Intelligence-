import DashboardLayout from "../components/layout/DashboardLayout";
import PageHeader from "../components/ui/PageHeader";
import PropertyIntakeForm from "../components/property/PropertyIntakeForm";

export default function Intake() {
  return (
    <DashboardLayout>
      <PageHeader
        title="Property Intake"
        subtitle="Paste an address, APN, or property link to begin analysis."
      />

      <PropertyIntakeForm />
    </DashboardLayout>
  );
}