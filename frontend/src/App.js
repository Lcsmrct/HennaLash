import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ContactPage from "./pages/ContactPage";
import GalleryPage from "./pages/GalleryPage";
import PricingPage from "./pages/PricingPage";
import ReviewsPage from "./pages/ReviewsPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import PasswordResetPage from "./pages/PasswordResetPage";
import ClientDashboard from "./pages/ClientDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import BookingDetailsPage from "./pages/BookingDetailsPage";
import MaintenancePage from "./pages/MaintenancePage";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "./components/ui/toaster";
import MaintenanceGuard from "./components/MaintenanceGuard";

function App() {  
  return (
    <div className="App">
      <AuthProvider>
        <MaintenanceGuard>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/galerie" element={<GalleryPage />} />
              <Route path="/tarifs" element={<PricingPage />} />
              <Route path="/avis" element={<ReviewsPage />} />
              <Route path="/connexion" element={<LoginPage />} />
              <Route path="/inscription" element={<RegisterPage />} />
              <Route path="/mot-de-passe-oublie" element={<PasswordResetPage />} />
              <Route path="/mon-espace" element={<ClientDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/maintenance" element={<MaintenancePage />} />
              <Route path="/reserver/:slotId" element={<BookingDetailsPage />} />
              {/* Keep legacy route for backward compatibility */}
              <Route path="/deconnexion" element={<HomePage />} />
            </Routes>
          </BrowserRouter>
          <Toaster />
        </MaintenanceGuard>
      </AuthProvider>
    </div>
  );
}

export default App;