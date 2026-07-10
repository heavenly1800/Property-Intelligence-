import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div
      style={{
        width: 240,
        background: "#1E1E1E",
        color: "white",
        minHeight: "100vh",
        padding: 20,
      }}
    >
      <h2>Property Intelligence</h2>

      <hr />

      <p><Link to="/" style={{color:"white"}}>Dashboard</Link></p>

      <p><Link to="/properties" style={{color:"white"}}>Properties</Link></p>

      <p><Link to="/settings" style={{color:"white"}}>Settings</Link></p>
    </div>
  );
}