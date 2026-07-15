import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Properties from "./pages/Properties";
import PropertyDetail from "./pages/PropertyDetail";
import  Intake  from "./pages/Intake";
import Settings from "./pages/Settings";
import Share from "./pages/Share";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/properties"
          element={<Properties />}
        />

        <Route
          path="/properties/:id"
          element={<PropertyDetail />}
        />

        <Route
    path="/intake"
    element={<Intake />}
/>

        <Route
          path="/settings"
          element={<Settings />}
        />
        <Route path="/share" element={<Share />} />
      </Routes>
    </BrowserRouter>
  );
}
