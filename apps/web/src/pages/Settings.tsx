import DashboardLayout from "../components/layout/DashboardLayout";
import CommunicationTemplates from "../components/settings/CommunicationTemplates";

export default function Settings() {
  return (
    <DashboardLayout>
      <h1>Settings</h1>
      <CommunicationTemplates />
    </DashboardLayout>
  );
}
