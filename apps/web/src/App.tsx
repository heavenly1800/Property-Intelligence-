import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Properties from "./pages/Properties";
import PropertyDetail from "./pages/PropertyDetail";
import  Intake  from "./pages/Intake";
import Settings from "./pages/Settings";
import Share from "./pages/Share";
import NotificationsPage from "./pages/Notifications";
import SignIn from "./pages/SignIn";
import UpdatePassword from "./pages/UpdatePassword";
import AcceptInvitation from "./pages/AcceptInvitation";
import ProtectedRoute from "./components/auth/ProtectedRoute";


export default function App() {
  return (
    <BrowserRouter>
      <Routes><Route path="/sign-in" element={<SignIn/>}/><Route path="/update-password" element={<UpdatePassword/>}/><Route path="/invitations/accept" element={<AcceptInvitation/>}/>
        <Route
          path="/"
          element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
        />

        <Route
          path="/properties"
          element={<ProtectedRoute><Properties /></ProtectedRoute>}
        />

        <Route
          path="/properties/:id"
          element={<ProtectedRoute><PropertyDetail /></ProtectedRoute>}
        />

        <Route
    path="/intake"
    element={<ProtectedRoute><Intake /></ProtectedRoute>}
/>

        <Route
          path="/settings"
          element={<ProtectedRoute><Settings /></ProtectedRoute>}
        />
        <Route path="/share" element={<ProtectedRoute><Share /></ProtectedRoute>} />
        <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
