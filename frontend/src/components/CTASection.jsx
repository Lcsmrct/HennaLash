import React from 'react';
import { Button } from './ui/button';
import { mockData } from '../mock';

const CTASection = () => {
  const { cta } = mockData;

  const handleClick = () => {
    window.location.href = '/reserver';
  };

  return (
    <section className="py-20 bg-gradient-to-r from-orange-600 to-orange-700">
      <div className="max-w-4xl mx-auto text-center px-6">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          {cta.title}
        </h2>
        <p className="text-xl text-white/90 mb-8 leading-relaxed">
          {cta.description}
        </p>
        <Button 
          onClick={handleClick}
          className="bg-white text-orange-600 hover:bg-orange-50 px-8 py-4 text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg"
        >
          {cta.buttonText}
        </Button>
      </div>
    </section>
  );
};

export default CTASection;