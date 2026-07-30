import DashboardLayout from "../components/layout/DashboardLayout";
import CommunicationTemplates from "../components/settings/CommunicationTemplates";
import TeamSettings from "../components/settings/TeamSettings";

export default function Settings() {
  return (
    <DashboardLayout>
      <h1>Settings</h1>
      <TeamSettings />
      <CommunicationTemplates />
    </DashboardLayout>
  );
}
