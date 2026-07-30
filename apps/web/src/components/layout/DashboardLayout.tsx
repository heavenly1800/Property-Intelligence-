import type { ReactNode } from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { useAuth } from "../../context/AuthContext";

type Props = {
  children: ReactNode;
};

export default function DashboardLayout({ children }: Props) {
  const {role}=useAuth();
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div style={{ flex: 1 }}>
        <Topbar />

        <div className={`role-${role??"unknown"}`} style={{ padding: 30 }}>
          {children}
        </div>
      </div>
    </div>
  );
}
