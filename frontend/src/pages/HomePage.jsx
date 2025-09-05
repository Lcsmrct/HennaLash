import React from 'react';
import Navigation from '../components/Navigation';
import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import CTASection from '../components/CTASection';
import PricingSection from '../components/PricingSection';
import TestimonialsSection from '../components/TestimonialsSection';

const HomePage = () => {
  return (
    <div className="min-h-screen">
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      <CTASection />
      <PricingSection />
      <TestimonialsSection />
    </div>
  );
};

export default HomePage;