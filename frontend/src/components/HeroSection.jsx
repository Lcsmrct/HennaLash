import React from 'react';
import { Button } from './ui/button';
import { mockData } from '../mock';

const HeroSection = () => {
  const { hero } = mockData;

  const handlePrimaryClick = () => {
    window.location.href = '/connexion';
  };

  const handleSecondaryClick = () => {
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('${hero.backgroundImage}')`,
        }}
      >
        {/* Dark overlay */}
        <div className="absolute inset-0 bg-black/40"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-4">
          {hero.title}
          <br />
          <span className="text-orange-400">{hero.subtitle}</span>
        </h1>
        
        <p className="text-lg md:text-xl text-white/90 mb-8 max-w-2xl mx-auto leading-relaxed">
          {hero.description}
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button 
            onClick={handlePrimaryClick}
            className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-3 text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            {hero.primaryButton}
          </Button>
          
          <Button 
            onClick={handleSecondaryClick}
            variant="outline" 
            className="border-white text-white hover:bg-white hover:text-gray-900 px-8 py-3 text-lg font-semibold transition-all duration-300 transform hover:scale-105 bg-transparent"
          >
            {hero.secondaryButton}
          </Button>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-white/50 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-white/50 rounded-full mt-2 animate-pulse"></div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;