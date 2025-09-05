import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ContactPage from "./pages/ContactPage";
import GalleryPage from "./pages/GalleryPage";
import { Toaster } from "./components/ui/toaster";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/reserver" element={<ContactPage />} />
          <Route path="/galerie" element={<GalleryPage />} />
          <Route path="/tarifs" element={<HomePage />} />
          <Route path="/avis" element={<HomePage />} />
          <Route path="/mon-espace" element={<HomePage />} />
          <Route path="/deconnexion" element={<HomePage />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;