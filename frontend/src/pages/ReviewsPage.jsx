import React, { useState } from 'react';
import { ArrowLeft, Star, Heart, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { mockData } from '../mock';

const ReviewsPage = () => {
  const { testimonials } = mockData;
  const [selectedService, setSelectedService] = useState('Tous');

  const services = ['Tous', 'Henné Simple', 'Henné Traditionnel', 'Henné Mariée', 'Atelier Groupe'];

  const filteredReviews = selectedService === 'Tous' 
    ? testimonials.reviews 
    : testimonials.reviews.filter(review => review.service.includes(selectedService));

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

  const additionalReviews = [
    {
      id: 7,
      name: "Yasmine T.",
      timeAgo: "Il y a 1 semaine",
      rating: 5,
      avatar: "YT",
      review: "Absolument parfait ! J'ai pris la formule traditionnelle pour mon anniversaire et le résultat était magnifique. L'artiste a su créer exactement ce que j'imaginais. Les motifs sont fins et détaillés, vraiment du travail d'artiste.",
      service: "Henné Traditionnel"
    },
    {
      id: 8,
      name: "Khadija B.",
      timeAgo: "Il y a 2 semaines",
      rating: 5,
      avatar: "KB",
      review: "Service exceptionnel du début à la fin ! Pour mon mariage, j'ai eu droit à un service complet avec des motifs traditionnels magnifiques. L'équipe est professionnelle et l'ambiance très relaxante. Mes invitées n'arrêtaient pas de complimenter !",
      service: "Henné Mariée"
    },
    {
      id: 9,
      name: "Sophie L.",
      timeAgo: "Il y a 3 semaines",
      rating: 5,
      avatar: "SL",
      review: "Première expérience avec le henné et je suis conquise ! Le design simple était parfait pour débuter. L'artiste m'a bien expliqué les soins à apporter et le henné a duré plus de 2 semaines. Je reviendrai certainement !",
      service: "Henné Simple"
    }
  ];

  const allReviews = [...testimonials.reviews, ...additionalReviews];
  const displayReviews = selectedService === 'Tous' 
    ? allReviews 
    : allReviews.filter(review => review.service.includes(selectedService));

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      <Navigation />
      
      <div className="pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-6 py-16">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <Link 
              to="/" 
              className="flex items-center gap-2 text-orange-600 hover:text-orange-700 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Retour à l'accueil
            </Link>
          </div>

          {/* Title */}
          <div className="text-center mb-16">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              {testimonials.title}
            </h1>
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

          {/* Service Filters */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <Filter className="w-5 h-5 text-gray-400 mt-2" />
            {services.map((service) => (
              <button
                key={service}
                onClick={() => setSelectedService(service)}
                className={`px-6 py-2 rounded-full font-medium transition-all duration-300 ${
                  selectedService === service
                    ? 'bg-orange-600 text-white transform scale-105'
                    : 'bg-white text-gray-700 hover:bg-orange-100 hover:text-orange-600 shadow-md'
                }`}
              >
                {service}
              </button>
            ))}
          </div>

          {/* Reviews Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            {displayReviews.map((review) => (
              <Card key={review.id} className="bg-white shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
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
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-orange-600 border-orange-600">
                      {review.service}
                    </Badge>
                    <button className="text-red-500 hover:text-red-600 transition-colors">
                      <Heart className="w-4 h-4" />
                    </button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Stats Section */}
          <div className="grid md:grid-cols-4 gap-8 mb-16 text-center">
            {testimonials.stats.map((stat, index) => (
              <div key={index} className="group bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-all duration-300">
                <div className="text-5xl md:text-6xl font-bold text-orange-600 mb-2 group-hover:scale-110 transition-transform duration-300">
                  {stat.number}
                </div>
                <p className="text-lg text-gray-600 font-medium">
                  {stat.label}
                </p>
              </div>
            ))}
            <div className="group bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-all duration-300">
              <div className="text-5xl md:text-6xl font-bold text-orange-600 mb-2 group-hover:scale-110 transition-transform duration-300">
                9+
              </div>
              <p className="text-lg text-gray-600 font-medium">
                Avis récents
              </p>
            </div>
          </div>

          {/* Detailed Ratings */}
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-16">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Détail des Évaluations</h3>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-700 w-20">Qualité</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div className="bg-orange-600 h-2 rounded-full" style={{width: '98%'}}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">4.9/5</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-700 w-20">Service</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div className="bg-orange-600 h-2 rounded-full" style={{width: '96%'}}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">4.8/5</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-700 w-20">Durabilité</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div className="bg-orange-600 h-2 rounded-full" style={{width: '94%'}}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">4.7/5</span>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-700 w-20">Créativité</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div className="bg-orange-600 h-2 rounded-full" style={{width: '100%'}}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">5.0/5</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-700 w-20">Propreté</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div className="bg-orange-600 h-2 rounded-full" style={{width: '100%'}}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">5.0/5</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-700 w-20">Rapport qualité/prix</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div className="bg-orange-600 h-2 rounded-full" style={{width: '92%'}}></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">4.6/5</span>
                </div>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="text-center bg-gradient-to-r from-orange-600 to-orange-700 rounded-2xl shadow-xl p-12 text-white">
            <h2 className="text-3xl font-bold mb-4">
              Rejoignez Nos Clientes Satisfaites
            </h2>
            <p className="text-xl text-orange-100 mb-8 max-w-2xl mx-auto">
              Découvrez pourquoi nos clientes nous font confiance pour leurs créations au henné. 
              Réservez votre séance et vivez une expérience exceptionnelle.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/reserver"
                className="inline-flex items-center gap-2 bg-white text-orange-600 px-8 py-4 rounded-lg font-semibold hover:bg-orange-50 transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                Réserver Maintenant
              </Link>
              <Link
                to="/tarifs"
                className="inline-flex items-center gap-2 border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-orange-600 transition-all duration-300 transform hover:scale-105"
              >
                Voir Nos Tarifs
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReviewsPage;