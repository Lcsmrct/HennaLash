import React, { useState, useEffect } from 'react';
import { Phone, Mail, MapPin, Clock } from 'lucide-react';
import Navigation from '../components/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import { useToast } from '../hooks/use-toast';
import { mockData } from '../mock';

const ContactPage = () => {
  const { contact } = mockData;
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    service: '',
    date: '',
    time: '',
    location: '',
    message: ''
  });

  // Pre-select service if coming from pricing
  useEffect(() => {
    const selectedPlan = localStorage.getItem('selectedPlan');
    if (selectedPlan) {
      const serviceMap = {
        'Henné Simple': 'Henné Simple - 25€',
        'Henné Traditionnel': 'Henné Traditionnel - 45€',
        'Henné Mariée': 'Henné Mariée - 120€'
      };
      setFormData(prev => ({ 
        ...prev, 
        service: serviceMap[selectedPlan] || '' 
      }));
      localStorage.removeItem('selectedPlan');
    }
  }, []);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Basic validation
    const requiredFields = ['fullName', 'email', 'phone', 'service', 'date', 'time'];
    const missingFields = requiredFields.filter(field => !formData[field]);
    
    if (missingFields.length > 0) {
      toast({
        title: "Erreur",
        description: "Veuillez remplir tous les champs obligatoires.",
        variant: "destructive"
      });
      return;
    }

    // Mock submission
    console.log('Form submitted:', formData);
    
    toast({
      title: "Demande envoyée !",
      description: "Nous vous contacterons dans les 24h pour confirmer votre rendez-vous.",
    });

    // Reset form
    setFormData({
      fullName: '',
      email: '',
      phone: '',
      service: '',
      date: '',
      time: '',
      location: '',
      message: ''
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      <Navigation />
      
      <div className="pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-6 py-16">
          {/* Title */}
          <div className="text-center mb-16">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              {contact.title}
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
              {contact.subtitle}
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-12">
            {/* Reservation Form */}
            <div className="lg:col-span-2">
              <Card className="shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl text-gray-900">
                    Formulaire de Réservation
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Name and Email */}
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="fullName" className="text-gray-700">
                          Nom complet *
                        </Label>
                        <Input
                          id="fullName"
                          type="text"
                          placeholder="Votre nom"
                          value={formData.fullName}
                          onChange={(e) => handleInputChange('fullName', e.target.value)}
                          className="bg-white border-gray-300 focus:border-orange-600"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email" className="text-gray-700">
                          Email *
                        </Label>
                        <Input
                          id="email"
                          type="email"
                          placeholder="votre@email.com"
                          value={formData.email}
                          onChange={(e) => handleInputChange('email', e.target.value)}
                          className="bg-white border-gray-300 focus:border-orange-600"
                        />
                      </div>
                    </div>

                    {/* Phone */}
                    <div className="space-y-2">
                      <Label htmlFor="phone" className="text-gray-700">
                        Téléphone *
                      </Label>
                      <Input
                        id="phone"
                        type="tel"
                        placeholder="06 12 34 56 78"
                        value={formData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className="bg-white border-gray-300 focus:border-orange-600"
                      />
                    </div>

                    {/* Service */}
                    <div className="space-y-2">
                      <Label className="text-gray-700">Service souhaité *</Label>
                      <Select value={formData.service} onValueChange={(value) => handleInputChange('service', value)}>
                        <SelectTrigger className="bg-white border-gray-300 focus:border-orange-600">
                          <SelectValue placeholder="Choisissez votre service" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Henné Simple - 25€">Henné Simple - 25€</SelectItem>
                          <SelectItem value="Henné Traditionnel - 45€">Henné Traditionnel - 45€</SelectItem>
                          <SelectItem value="Henné Mariée - 120€">Henné Mariée - 120€</SelectItem>
                          <SelectItem value="Atelier Groupe">Atelier Groupe</SelectItem>
                          <SelectItem value="Autre demande">Autre demande</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Date and Time */}
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="date" className="text-gray-700">
                          Date souhaitée *
                        </Label>
                        <Input
                          id="date"
                          type="date"
                          value={formData.date}
                          onChange={(e) => handleInputChange('date', e.target.value)}
                          className="bg-white border-gray-300 focus:border-orange-600"
                          min={new Date().toISOString().split('T')[0]}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-gray-700">Heure préférée *</Label>
                        <Select value={formData.time} onValueChange={(value) => handleInputChange('time', value)}>
                          <SelectTrigger className="bg-white border-gray-300 focus:border-orange-600">
                            <SelectValue placeholder="Choisir un horaire" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="9h00">9h00</SelectItem>
                            <SelectItem value="10h00">10h00</SelectItem>
                            <SelectItem value="11h00">11h00</SelectItem>
                            <SelectItem value="14h00">14h00</SelectItem>
                            <SelectItem value="15h00">15h00</SelectItem>
                            <SelectItem value="16h00">16h00</SelectItem>
                            <SelectItem value="17h00">17h00</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Location */}
                    <div className="space-y-2">
                      <Label className="text-gray-700">Lieu souhaité</Label>
                      <Select value={formData.location} onValueChange={(value) => handleInputChange('location', value)}>
                        <SelectTrigger className="bg-white border-gray-300 focus:border-orange-600">
                          <SelectValue placeholder="Choisir le lieu" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="En salon">En salon</SelectItem>
                          <SelectItem value="À domicile">À domicile</SelectItem>
                          <SelectItem value="Événement">Événement</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Message */}
                    <div className="space-y-2">
                      <Label htmlFor="message" className="text-gray-700">
                        Message (optionnel)
                      </Label>
                      <Textarea
                        id="message"
                        rows={4}
                        placeholder="Décrivez vos souhaits particuliers, motifs préférés..."
                        value={formData.message}
                        onChange={(e) => handleInputChange('message', e.target.value)}
                        className="bg-white border-gray-300 focus:border-orange-600 resize-none"
                      />
                    </div>

                    {/* Submit Button */}
                    <Button 
                      type="submit"
                      className="w-full bg-orange-600 hover:bg-orange-700 text-white py-3 text-lg font-semibold transition-all duration-300 transform hover:scale-105"
                    >
                      Envoyer ma Demande de Réservation
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Contact Info */}
            <div className="space-y-8">
              {/* Direct Contact */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl text-orange-600 flex items-center gap-2">
                    <Phone className="w-5 h-5" />
                    Contact Direct
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-3 text-gray-700">
                    <Phone className="w-5 h-5 text-orange-600" />
                    <span>06 12 34 56 78</span>
                  </div>
                  <div className="flex items-center gap-3 text-gray-700">
                    <Mail className="w-5 h-5 text-orange-600" />
                    <span>contact@henne-artisanal.fr</span>
                  </div>
                  <div className="flex items-start gap-3 text-gray-700">
                    <MapPin className="w-5 h-5 text-orange-600 mt-1" />
                    <div>
                      <p>123 Rue de la Beauté</p>
                      <p>75001 Paris</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Opening Hours */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl text-orange-600 flex items-center gap-2">
                    <Clock className="w-5 h-5" />
                    Horaires d'Ouverture
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between text-gray-700">
                    <span>Lundi - Vendredi</span>
                    <span className="font-medium">9h - 18h</span>
                  </div>
                  <div className="flex justify-between text-gray-700">
                    <span>Samedi</span>
                    <span className="font-medium">9h - 17h</span>
                  </div>
                  <div className="flex justify-between text-gray-700">
                    <span>Dimanche</span>
                    <span className="font-medium">Sur RDV</span>
                  </div>
                </CardContent>
              </Card>

              {/* Additional Info */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="text-xl text-orange-600">
                    À Savoir
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li>• Confirmation par SMS dans les 24h</li>
                    <li>• Possibilité d'annulation jusqu'à 24h avant</li>
                    <li>• Paiement en espèces ou par carte</li>
                    <li>• Henné 100% naturel et végétal</li>
                    <li>• Durée: 1 à 3 semaines selon la peau</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;