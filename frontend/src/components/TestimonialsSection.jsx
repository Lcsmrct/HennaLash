import React from 'react';
import { Star } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { mockData } from '../mock';

const TestimonialsSection = () => {
  const { testimonials } = mockData;

  const renderStars = (rating) => {
    return Array.from({ length: 5 }).map((_, index) => (
      <Star 
        key={index} 
        className={`w-4 h-4 ${
          index < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`} 
      />
    ));
  };

  return (
    <section id="testimonials" className="py-20 bg-gradient-to-b from-orange-50 to-white">
      <div className="max-w-7xl mx-auto px-6">
        {/* Title */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            {testimonials.title}
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed mb-6">
            {testimonials.subtitle}
          </p>
          
          {/* Rating */}
          <div className="flex items-center justify-center gap-2 mb-2">
            <span className="text-6xl font-bold text-orange-600">
              {testimonials.rating.score}
            </span>
            <div className="flex">
              {renderStars(5)}
            </div>
          </div>
          <p className="text-sm text-gray-500">
            {testimonials.rating.text}
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {testimonials.reviews.map((review) => (
            <Card key={review.id} className="bg-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <CardContent className="p-6">
                {/* Avatar and Info */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                    {review.avatar}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">
                      {review.name}
                    </h4>
                    <p className="text-sm text-gray-500">
                      {review.timeAgo}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="flex">
                      {renderStars(review.rating)}
                    </div>
                  </div>
                </div>

                {/* Review Text */}
                <p className="text-gray-700 leading-relaxed mb-4 text-sm">
                  "{review.review}"
                </p>

                {/* Service Badge */}
                <Badge variant="outline" className="text-orange-600 border-orange-600">
                  {review.service}
                </Badge>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-8 text-center">
          {testimonials.stats.map((stat, index) => (
            <div key={index} className="group">
              <div className="text-5xl md:text-6xl font-bold text-orange-600 mb-2 group-hover:scale-110 transition-transform duration-300">
                {stat.number}
              </div>
              <p className="text-lg text-gray-600 font-medium">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;