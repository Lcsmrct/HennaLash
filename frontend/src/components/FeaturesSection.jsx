import React from 'react';
import { MapPin, User, Star, Clock } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { mockData } from '../mock';

const FeaturesSection = () => {
  const { features } = mockData;

  const getIcon = (iconName) => {
    const iconProps = { className: "w-12 h-12 text-orange-600 mb-4 mx-auto" };
    
    switch (iconName) {
      case 'map-pin':
        return <MapPin {...iconProps} />;
      case 'user':
        return <User {...iconProps} />;
      case 'star':
        return <Star {...iconProps} />;
      case 'clock':
        return <Clock {...iconProps} />;
      default:
        return <Star {...iconProps} />;
    }
  };

  return (
    <section id="features" className="py-20 bg-gradient-to-b from-orange-50 to-white">
      <div className="max-w-7xl mx-auto px-6">
        {/* Title */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {features.title}
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
            {features.subtitle}
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.items.map((feature, index) => (
            <Card 
              key={index} 
              className="bg-white hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 border-0 shadow-lg"
            >
              <CardContent className="p-8 text-center">
                {getIcon(feature.icon)}
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;