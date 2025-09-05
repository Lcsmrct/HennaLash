import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ContactPage from "./pages/ContactPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/reserver" element={<ContactPage />} />
          <Route path="/tarifs" element={<HomePage />} />
          <Route path="/avis" element={<HomePage />} />
          <Route path="/galerie" element={<HomePage />} />
          <Route path="/mon-espace" element={<HomePage />} />
          <Route path="/deconnexion" element={<HomePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;