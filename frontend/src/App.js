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
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "./components/ui/toaster";
import MaintenancePage from "./components/MaintenancePage";
import { useMaintenance } from "./hooks/useMaintenance";

function App() {
  const { maintenanceStatus, loading } = useMaintenance();

  // Si en cours de vérification de maintenance, afficher un loading léger
  if (loading) {
    return (
      <div className="App">
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Chargement...</p>
          </div>
        </div>
      </div>
    );
  }

  // Si le site est en maintenance, afficher la page de maintenance
  if (maintenanceStatus.is_maintenance) {
    return (
      <div className="App">
        <MaintenancePage maintenanceInfo={maintenanceStatus} />
      </div>
    );
  }

  // Site normal
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<HomePage />} />

            <Route path="/galerie" element={<GalleryPage />} />
            <Route path="/tarifs" element={<PricingPage />} />
            <Route path="/avis" element={<ReviewsPage />} />
            <Route path="/connexion" element={<LoginPage />} />
            <Route path="/inscription" element={<RegisterPage />} />
            <Route path="/mon-espace" element={<ClientDashboard />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/reserver/:slotId" element={<BookingDetailsPage />} />
            {/* Keep legacy route for backward compatibility */}
            <Route path="/deconnexion" element={<HomePage />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </AuthProvider>
    </div>
  );
}

export default App;