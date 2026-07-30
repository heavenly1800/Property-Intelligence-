import NotificationCenter from "./NotificationCenter";
import { useAuth } from "../../context/AuthContext";
export default function Topbar() {
  const {organizations,organizationId,role,selectOrganization,signOut}=useAuth();
  return (
    <div
      style={{
        height: 70,
        borderBottom: "1px solid #ddd",
        display: "flex",
        alignItems: "center",
        padding: "0 30px",
        fontSize: 22,
        fontWeight: "bold",
      }}
    >
      <span>Opportunity Command Center</span><span style={{marginLeft:"auto",display:"flex",gap:10,alignItems:"center"}}><select className="viewer-safe" aria-label="Organization" value={organizationId??""} onChange={e=>selectOrganization(e.target.value)}>{organizations.map(x=><option key={x.organization_id} value={x.organization_id}>{x.organizations.name}</option>)}</select><small>{role}</small><NotificationCenter /><button className="viewer-safe" onClick={()=>void signOut()}>Sign out</button></span>
    </div>
  );
}
