import DashboardLayout from "../components/layout/DashboardLayout";

export default function Dashboard() {
  return (
    <DashboardLayout>

      <h1>Good Evening, Heavenly 👋</h1>

      <h2>Today's Opportunities</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4,1fr)",
          gap: 20,
          marginTop: 30,
        }}
      >
        <div style={{border:"1px solid #ddd",padding:20}}>
          <h3>Properties</h3>
          <h1>2</h1>
        </div>

        <div style={{border:"1px solid #ddd",padding:20}}>
          <h3>Average Score</h3>
          <h1>76</h1>
        </div>

        <div style={{border:"1px solid #ddd",padding:20}}>
          <h3>Wholesale Ready</h3>
          <h1>1</h1>
        </div>

        <div style={{border:"1px solid #ddd",padding:20}}>
          <h3>Needs Research</h3>
          <h1>1</h1>
        </div>

      </div>

    </DashboardLayout>
  );
}