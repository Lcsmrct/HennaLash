import React from 'react';
import { Heart, Star, Crown, Check } from 'lucide-react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { mockData } from '../mock';

const PricingSection = () => {
  const { pricing } = mockData;

  const getIcon = (iconName) => {
    const iconProps = { className: "w-8 h-8 text-orange-600" };
    
    switch (iconName) {
      case 'heart':
        return <Heart {...iconProps} />;
      case 'star':
        return <Star {...iconProps} />;
      case 'crown':
        return <Crown {...iconProps} />;
      default:
        return <Star {...iconProps} />;
    }
  };

  const handleReservation = (planName) => {
    // Store selected plan in localStorage for the contact form
    localStorage.setItem('selectedPlan', planName);
    window.location.href = '/reserver';
  };

  return (
    <section id="pricing" className="py-20 bg-gradient-to-b from-white to-orange-50">
      <div className="max-w-7xl mx-auto px-6">
        {/* Title */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {pricing.title}
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
            {pricing.subtitle}
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {pricing.plans.map((plan, index) => (
            <Card 
              key={index}
              className={`relative transition-all duration-300 transform hover:-translate-y-2 ${
                plan.popular 
                  ? 'border-2 border-orange-600 shadow-2xl scale-105' 
                  : 'border border-gray-200 shadow-lg hover:shadow-xl'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-orange-600 text-white px-4 py-1 text-sm font-semibold">
                    Plus Populaire
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pb-2">
                <div className="flex justify-center mb-4">
                  {getIcon(plan.icon)}
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h3>
                <div className="mb-2">
                  <span className="text-4xl font-bold text-orange-600">
                    {plan.price}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mb-4">
                  {plan.duration}
                </p>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {plan.description}
                </p>
              </CardHeader>

              <CardContent className="pt-6">
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700 text-sm">
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                <Button 
                  onClick={() => handleReservation(plan.name)}
                  className={`w-full py-3 font-semibold transition-all duration-300 ${
                    plan.popular
                      ? 'bg-orange-600 text-white hover:bg-orange-700 transform hover:scale-105'
                      : 'bg-gray-100 text-gray-700 hover:bg-orange-600 hover:text-white'
                  }`}
                >
                  {plan.buttonText}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PricingSection;