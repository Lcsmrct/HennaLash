import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/apiService';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Calendar, Clock, ArrowLeft, Instagram, MapPin, Users, MessageSquare } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import Navigation from '../components/Navigation';

const BookingDetailsPage = () => {
  const { user, isAuthenticated } = useAuth();
  const { slotId } = useParams();
  const navigate = useNavigate();
  const [slot, setSlot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bookingForm, setBookingForm] = useState({
    service_name: 'Simple', // Service par défaut
    service_price: 8, // Prix par défaut
    instagram: '',
    lieu: '',
    nombre_personnes: '1',
    informations_supplementaires: ''
  });

  // Services disponibles
const services = [
  { 
    name: 'Très simple', 
    price: 5, 
    priceDisplay: '5€ par main',
    duration: '10-15 min', 
    description: 'Design sur un doigt' 
  },
  { 
    name: 'Simple', 
    price: 8, 
    priceDisplay: '8€ par main',
    duration: '20-30 min', 
    description: 'Design simple sur une main' 
  },
  { 
    name: 'Chargé', 
    price: 12, 
    priceDisplay: '12€ par main',
    duration: '45 min - 1h', 
    description: 'Design sur main chargé' 
  },
  { 
    name: 'Mariée', 
    price: 20, 
    priceDisplay: '20€ par main + avant-bras',
    duration: '1h - 1h30', 
    description: 'main et avant-bras' 
  }
];

  // Redirect if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/connexion" replace />;
  }

  if (user?.role === 'admin') {
    return <Navigate to="/admin" replace />;
  }

  useEffect(() => {
    fetchSlotDetails();
  }, [slotId]);

  const fetchSlotDetails = async () => {
    try {
      setLoading(true);
      const availableSlots = await apiService.getSlots(true);
      const selectedSlot = availableSlots.find(s => s.id === slotId);
      
      if (!selectedSlot) {
        toast({
          title: "Erreur",
          description: "Créneau non trouvé ou plus disponible",
          variant: "destructive"
        });
        navigate('/mon-espace');
        return;
      }
      
      setSlot(selectedSlot);
    } catch (error) {
      console.error('Error fetching slot details:', error);
      toast({
        title: "Erreur",
        description: "Impossible de charger les détails du créneau",
        variant: "destructive"
      });
      navigate('/mon-espace');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation: le lieu est obligatoire
    if (!bookingForm.lieu) {
      toast({
        title: "Champ obligatoire",
        description: "Veuillez sélectionner un lieu pour votre rendez-vous",
        variant: "destructive"
      });
      return;
    }
    
    try {
      // Combiner toutes les informations dans les notes avec un formatage amélioré
      const notesArray = [];
      
      if (bookingForm.instagram) {
        notesArray.push(`📱 Instagram: ${bookingForm.instagram}`);
      }
      
      if (bookingForm.lieu) {
        notesArray.push(`📍 Lieu: ${bookingForm.lieu}`);
      }
      
      notesArray.push(`👥 Nombre de personnes: ${bookingForm.nombre_personnes}`);
      
      if (bookingForm.informations_supplementaires) {
        notesArray.push(`ℹ️ Informations supplémentaires:\n${bookingForm.informations_supplementaires}`);
      }
      
      const notes = notesArray.join('\n\n');

      await apiService.createAppointment({
        slot_id: slotId,
        service_name: bookingForm.service_name,
        service_price: bookingForm.service_price,
        notes: notes
      });
      
      toast({
        title: "Succès",
        description: "Rendez-vous réservé avec succès !"
      });
      
      navigate('/mon-espace');
    } catch (error) {
      console.error('Error booking appointment:', error);
      toast({
        title: "Erreur",
        description: error.response?.data?.detail || "Impossible de réserver le rendez-vous",
        variant: "destructive"
      });
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          <p className="mt-4">Chargement...</p>
        </div>
      </div>
    );
  }

  if (!slot) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50 relative">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-gradient-to-r from-orange-100/20 via-transparent to-amber-100/20"></div>
      <div className="absolute inset-0" style={{
        backgroundImage: `radial-gradient(circle at 25% 25%, rgba(251, 146, 60, 0.05) 0%, transparent 50%), 
                         radial-gradient(circle at 75% 75%, rgba(245, 158, 11, 0.05) 0%, transparent 50%)`
      }}></div>
      
      <Navigation />
      
      <div className="container mx-auto px-3 sm:px-4 py-6 sm:py-8 relative z-10">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 mb-6 sm:mb-8">
            <Button 
              variant="outline" 
              onClick={() => navigate('/mon-espace')}
              className="w-auto bg-white/80 backdrop-blur-sm border-orange-200 hover:bg-orange-50/80 hover:border-orange-300 hover:scale-105 transition-all duration-200"
            >
              <ArrowLeft className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
              <span className="text-xs sm:text-sm">Retour</span>
            </Button>
            <div className="w-full sm:w-auto">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold bg-gradient-to-r from-orange-600 via-amber-600 to-orange-700 bg-clip-text text-transparent leading-tight">
                ✨ Finaliser la Réservation
              </h1>
              <p className="text-sm sm:text-base text-gray-700 mt-1 font-medium">Ajoutez vos informations personnalisées</p>
            </div>
          </div>

          {/* Slot Details Card */}
          <div className="mb-6 sm:mb-8 bg-gradient-to-br from-white/90 via-white/80 to-orange-50/90 backdrop-blur-xl rounded-2xl border border-orange-200/50 shadow-xl hover:shadow-2xl transition-all duration-300">
            <div className="p-4 sm:p-6 border-b border-orange-100/50 bg-gradient-to-r from-orange-500/10 via-amber-500/10 to-orange-500/10 rounded-t-2xl">
              <h2 className="flex items-center text-base sm:text-lg font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                <Calendar className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-orange-500" />
                📅 Détails du Créneau
              </h2>
            </div>
            <div className="p-4 sm:p-6">
              <div className="space-y-3 sm:space-y-4">
                <h3 className="font-bold text-lg sm:text-xl text-gray-800">HennaLash</h3>
                <div className="flex items-center text-sm sm:text-base text-gray-700 font-medium">
                  <Calendar className="mr-3 h-4 w-4 sm:h-5 sm:w-5 text-orange-500 flex-shrink-0" />
                  <span className="truncate">{formatDate(slot.date)}</span>
                </div>
                <div className="flex items-center text-sm sm:text-base text-gray-700 font-medium">
                  <Clock className="mr-3 h-4 w-4 sm:h-5 sm:w-5 text-amber-500 flex-shrink-0" />
                  <span>{formatTime(slot.start_time)}</span>
                </div>
                <div className="bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl p-3 sm:p-4 text-center">
                  <p className="text-xl sm:text-2xl font-bold text-white">
                    💰 {bookingForm.service_price}€
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Booking Form */}
          <div className="bg-gradient-to-br from-white/90 via-white/85 to-orange-50/90 backdrop-blur-xl rounded-2xl border border-orange-200/50 shadow-xl hover:shadow-2xl transition-all duration-300">
            <div className="p-4 sm:p-6 border-b border-orange-100/50 bg-gradient-to-r from-orange-500/10 via-amber-500/10 to-orange-500/10 rounded-t-2xl">
              <h2 className="text-base sm:text-lg font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                📋 Informations de Réservation
              </h2>
              <p className="text-sm sm:text-base text-gray-700 mt-1 font-medium">
                Veuillez remplir ces informations pour personnaliser votre rendez-vous
              </p>
            </div>
            <div className="p-4 sm:p-6">
              <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-8">
                {/* Service Selection */}
                <div className="space-y-4">
                  <Label className="text-base sm:text-lg font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent flex items-center">
                    🎨 Choisissez votre service
                  </Label>
                  <div className="grid gap-3 sm:gap-4">
                    {services.map((service) => (
                      <div 
                        key={service.name}
                        className={`group p-4 sm:p-5 rounded-xl cursor-pointer transition-all duration-300 hover:scale-[1.02] ${
                          bookingForm.service_name === service.name 
                            ? 'bg-gradient-to-r from-orange-100 to-amber-100 border-2 border-orange-400 shadow-lg ring-2 ring-orange-300/50' 
                            : 'bg-white/70 backdrop-blur-sm border-2 border-orange-200/50 hover:border-orange-300 hover:shadow-md hover:bg-orange-50/50'
                        }`}
                        onClick={() => setBookingForm({
                          ...bookingForm, 
                          service_name: service.name, 
                          service_price: service.price
                        })}
                      >
                        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 sm:gap-0">
                          <div className="flex-1 min-w-0">
                            <h3 className="font-bold text-base sm:text-lg text-gray-800 group-hover:text-orange-700 transition-colors">
                              {service.name}
                            </h3>
                            <p className="text-sm sm:text-base text-gray-600 break-words font-medium">
                              {service.description}
                            </p>
                            <p className="text-xs sm:text-sm text-gray-500 font-medium mt-1">⏱️ {service.duration}</p>
                          </div>
                          <div className="text-left sm:text-right flex-shrink-0">
                            <div className="bg-gradient-to-r from-orange-500 to-amber-500 text-white px-3 py-2 rounded-lg">
                              <p className="text-lg sm:text-xl font-bold">{service.priceDisplay}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <Label htmlFor="instagram" className="flex items-center text-sm sm:text-base font-semibold text-gray-700">
                    <Instagram className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-pink-500" />
                    📱 Instagram (optionnel)
                  </Label>
                  <Input
                    id="instagram"
                    value={bookingForm.instagram}
                    onChange={(e) => setBookingForm({...bookingForm, instagram: e.target.value})}
                    placeholder="@votre_instagram"
                    className="h-11 sm:h-12 text-sm sm:text-base bg-white/80 backdrop-blur-sm border-orange-200 focus:border-orange-400 focus:ring-orange-300/50 hover:bg-white/90 transition-all"
                  />
                </div>

                <div className="space-y-3">
                  <Label htmlFor="lieu" className="flex items-center text-sm sm:text-base font-semibold text-gray-700">
                    <MapPin className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-red-500" />
                    📍 Lieu souhaité <span className="bg-gradient-to-r from-red-500 to-pink-500 text-white px-2 py-1 rounded-full text-xs ml-2">Obligatoire</span>
                  </Label>
                  <Select 
                    value={bookingForm.lieu} 
                    onValueChange={(value) => setBookingForm({...bookingForm, lieu: value})}
                    required
                  >
                    <SelectTrigger className={`h-11 sm:h-12 bg-white/80 backdrop-blur-sm border-orange-200 focus:border-orange-400 hover:bg-white/90 transition-all ${!bookingForm.lieu ? 'border-red-300 ring-2 ring-red-200/50' : ''}`}>
                      <SelectValue placeholder="🏠 Choisissez le lieu *" />
                    </SelectTrigger>
                    <SelectContent className="bg-white/95 backdrop-blur-sm">
                      <SelectItem value="salon" className="hover:bg-orange-50">🏠 Chez moi</SelectItem>
                      <SelectItem value="domicile" className="hover:bg-orange-50">🚗 Chez vous</SelectItem>
                      <SelectItem value="evenement" className="hover:bg-orange-50">🎉 Autre</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-3">
                  <Label htmlFor="nombre_personnes" className="flex items-center text-sm sm:text-base font-semibold text-gray-700">
                    <Users className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-blue-500" />
                    👥 Nombre de personnes
                  </Label>
                  <Select 
                    value={bookingForm.nombre_personnes} 
                    onValueChange={(value) => setBookingForm({...bookingForm, nombre_personnes: value})}
                  >
                    <SelectTrigger className="h-11 sm:h-12 bg-white/80 backdrop-blur-sm border-orange-200 focus:border-orange-400 hover:bg-white/90 transition-all">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white/95 backdrop-blur-sm">
                      <SelectItem value="1" className="hover:bg-orange-50">1️⃣ 1 personne</SelectItem>
                      <SelectItem value="2" className="hover:bg-orange-50">2️⃣ 2 personnes</SelectItem>
                      <SelectItem value="3" className="hover:bg-orange-50">3️⃣ 3 personnes</SelectItem>
                      <SelectItem value="4" className="hover:bg-orange-50">4️⃣ 4 personnes</SelectItem>
                      <SelectItem value="5+" className="hover:bg-orange-50">5️⃣+ 5+ personnes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-3">
                  <Label htmlFor="informations_supplementaires" className="text-sm sm:text-base font-semibold text-gray-700 flex items-center">
                    <MessageSquare className="mr-2 h-4 w-4 sm:h-5 sm:w-5 text-purple-500" />
                    💬 Informations supplémentaires
                  </Label>
                  <Textarea
                    id="informations_supplementaires"
                    value={bookingForm.informations_supplementaires}
                    onChange={(e) => setBookingForm({...bookingForm, informations_supplementaires: e.target.value})}
                    placeholder="Exemple: Mariages, henné, soirée entre copines..."
                    className="min-h-[80px] sm:min-h-[100px] text-sm sm:text-base bg-white/80 backdrop-blur-sm border-orange-200 focus:border-orange-400 focus:ring-orange-300/50 hover:bg-white/90 transition-all resize-none"
                  />
                </div>

                <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 pt-4">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => navigate('/mon-espace')}
                    className="flex-1 h-12 sm:h-14 text-sm sm:text-base font-semibold bg-white/80 backdrop-blur-sm border-2 border-gray-300 hover:bg-gray-50/80 hover:border-gray-400 hover:scale-105 transition-all duration-200"
                  >
                    ❌ Annuler
                  </Button>
                  <Button 
                    type="submit" 
                    className="flex-1 h-12 sm:h-14 text-sm sm:text-base font-bold bg-gradient-to-r from-orange-500 via-amber-500 to-orange-600 hover:from-orange-600 hover:via-amber-600 hover:to-orange-700 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 border-0"
                  >
                    ✅ Confirmer la Réservation
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookingDetailsPage;