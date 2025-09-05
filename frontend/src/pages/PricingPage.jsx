import React from 'react';
import { ArrowLeft, Heart, Star, Crown, Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import { Card, CardContent, CardHeader } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { mockData } from '../mock';

const PricingPage = () => {
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
              {pricing.title}
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
              {pricing.subtitle}
            </p>
          </div>

          {/* Pricing Cards */}
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
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

          {/* Additional Information */}
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {/* FAQ Section */}
            <Card className="shadow-lg">
              <CardHeader>
                <h3 className="text-2xl font-bold text-gray-900">Questions Fréquentes</h3>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Combien de temps dure le henné ?</h4>
                  <p className="text-gray-600 text-sm">Le henné dure généralement entre 1 à 3 semaines selon votre type de peau et les soins apportés.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Le henné est-il naturel ?</h4>
                  <p className="text-gray-600 text-sm">Oui, nous utilisons exclusivement du henné 100% naturel et végétal, sans additifs chimiques.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Puis-je personnaliser mon design ?</h4>
                  <p className="text-gray-600 text-sm">Absolument ! Nous adaptons chaque création selon vos goûts et préférences personnelles.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Proposez-vous le service à domicile ?</h4>
                  <p className="text-gray-600 text-sm">Oui, pour la formule Henné Mariée et les événements spéciaux, nous nous déplaçons à domicile.</p>
                </div>
              </CardContent>
            </Card>

            {/* What's Included */}
            <Card className="shadow-lg">
              <CardHeader>
                <h3 className="text-2xl font-bold text-gray-900">Inclus dans Nos Services</h3>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Consultation Personnalisée</h4>
                    <p className="text-gray-600 text-sm">Discussion sur vos préférences et conseils de design</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Henné Premium</h4>
                    <p className="text-gray-600 text-sm">Produits de haute qualité pour des résultats durables</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Guide d'Entretien</h4>
                    <p className="text-gray-600 text-sm">Conseils pour optimiser la tenue de votre henné</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Garantie Satisfaction</h4>
                    <p className="text-gray-600 text-sm">Retouches gratuites si nécessaire dans les 48h</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900">Ambiance Relaxante</h4>
                    <p className="text-gray-600 text-sm">Environnement calme et professionnel</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* CTA Section */}
          <div className="text-center bg-gradient-to-r from-orange-600 to-orange-700 rounded-2xl shadow-xl p-12 text-white">
            <h2 className="text-3xl font-bold mb-4">
              Prête pour Votre Transformation ?
            </h2>
            <p className="text-xl text-orange-100 mb-8 max-w-2xl mx-auto">
              Choisissez votre formule et réservez dès maintenant pour vivre une expérience unique 
              de beauté naturelle avec nos créations au henné.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/reserver"
                className="inline-flex items-center gap-2 bg-white text-orange-600 px-8 py-4 rounded-lg font-semibold hover:bg-orange-50 transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                Réserver Maintenant
              </Link>
              <Link
                to="/galerie"
                className="inline-flex items-center gap-2 border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-orange-600 transition-all duration-300 transform hover:scale-105"
              >
                Voir Nos Créations
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;