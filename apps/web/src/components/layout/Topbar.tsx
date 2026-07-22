import NotificationCenter from "./NotificationCenter";
export default function Topbar() {
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
      <span>Opportunity Command Center</span><span style={{marginLeft:"auto"}}><NotificationCenter /></span>
    </div>
  );
}
