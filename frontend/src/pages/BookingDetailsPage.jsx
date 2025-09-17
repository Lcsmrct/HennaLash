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
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-3 sm:px-4 py-6 sm:py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 mb-6 sm:mb-8">
            <Button 
              variant="outline" 
              onClick={() => navigate('/mon-espace')}
              className="w-auto"
            >
              <ArrowLeft className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
              <span className="text-xs sm:text-sm">Retour</span>
            </Button>
            <div className="w-full sm:w-auto">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 leading-tight">
                Finaliser la Réservation
              </h1>
              <p className="text-sm sm:text-base text-gray-600 mt-1">Ajoutez vos informations personnalisées</p>
            </div>
          </div>

          {/* Slot Details Card */}
          <Card className="mb-6 sm:mb-8">
            <CardHeader className="pb-3 sm:pb-6">
              <CardTitle className="flex items-center text-base sm:text-lg">
                <Calendar className="mr-2 h-4 w-4 sm:h-5 sm:w-5" />
                Détails du Créneau
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 sm:space-y-3">
                <h3 className="font-semibold text-base sm:text-lg">{slot.service_name}</h3>
                <div className="flex items-center text-sm sm:text-base text-gray-600">
                  <Calendar className="mr-2 h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
                  <span className="truncate">{formatDate(slot.date)}</span>
                </div>
                <div className="flex items-center text-sm sm:text-base text-gray-600">
                  <Clock className="mr-2 h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
                  <span>{formatTime(slot.start_time)}</span>
                </div>
                <p className="text-xl sm:text-2xl font-bold text-orange-600 pt-1">
                  {bookingForm.service_price}€
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Booking Form */}
          <Card>
            <CardHeader className="pb-3 sm:pb-6">
              <CardTitle className="text-base sm:text-lg">Informations de Réservation</CardTitle>
              <CardDescription className="text-sm sm:text-base">
                Veuillez remplir ces informations pour personnaliser votre rendez-vous
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
                {/* Service Selection */}
                <div className="space-y-3">
                  <Label className="text-base sm:text-lg font-semibold">🎨 Choisissez votre service</Label>
                  <div className="grid gap-2 sm:gap-3">
                    {services.map((service) => (
                      <div 
                        key={service.name}
                        className={`p-3 sm:p-4 rounded-lg border-2 cursor-pointer transition-all ${
                          bookingForm.service_name === service.name 
                            ? 'border-orange-500 bg-orange-50' 
                            : 'border-gray-200 hover:border-orange-300'
                        }`}
                        onClick={() => setBookingForm({
                          ...bookingForm, 
                          service_name: service.name, 
                          service_price: service.price
                        })}
                      >
                        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 sm:gap-0">
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-sm sm:text-base">{service.name}</h3>
                            <p className="text-xs sm:text-sm text-gray-600 break-words">{service.description}</p>
                            <p className="text-xs text-gray-500">{service.duration}</p>
                          </div>
                          <div className="text-left sm:text-right flex-shrink-0">
                            <p className="text-lg sm:text-xl font-bold text-orange-600">{service.priceDisplay}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="instagram" className="flex items-center text-sm sm:text-base">
                    <Instagram className="mr-2 h-3 w-3 sm:h-4 sm:w-4" />
                    Instagram (optionnel)
                  </Label>
                  <Input
                    id="instagram"
                    value={bookingForm.instagram}
                    onChange={(e) => setBookingForm({...bookingForm, instagram: e.target.value})}
                    placeholder="@votre_instagram"
                    className="h-10 sm:h-11 text-sm sm:text-base"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lieu" className="flex items-center text-sm sm:text-base">
                    <MapPin className="mr-2 h-3 w-3 sm:h-4 sm:w-4" />
                    Lieu souhaité <span className="text-red-500 ml-1">*</span>
                  </Label>
                  <Select 
                    value={bookingForm.lieu} 
                    onValueChange={(value) => setBookingForm({...bookingForm, lieu: value})}
                    required
                  >
                    <SelectTrigger className={`h-10 sm:h-11 ${!bookingForm.lieu ? 'border-red-200 hover:border-red-300' : ''}`}>
                      <SelectValue placeholder="Choisissez le lieu *" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="salon">Chez moi</SelectItem>
                      <SelectItem value="domicile">Chez vous</SelectItem>
                      <SelectItem value="evenement">Autre</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nombre_personnes" className="flex items-center text-sm sm:text-base">
                    <Users className="mr-2 h-3 w-3 sm:h-4 sm:w-4" />
                    Nombre de personnes
                  </Label>
                  <Select 
                    value={bookingForm.nombre_personnes} 
                    onValueChange={(value) => setBookingForm({...bookingForm, nombre_personnes: value})}
                  >
                    <SelectTrigger className="h-10 sm:h-11">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1 personne</SelectItem>
                      <SelectItem value="2">2 personnes</SelectItem>
                      <SelectItem value="3">3 personnes</SelectItem>
                      <SelectItem value="4">4 personnes</SelectItem>
                      <SelectItem value="5+">5+ personnes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="informations_supplementaires" className="text-sm sm:text-base">
                    Informations supplémentaires
                  </Label>
                  <Textarea
                    id="informations_supplementaires"
                    value={bookingForm.informations_supplementaires}
                    onChange={(e) => setBookingForm({...bookingForm, informations_supplementaires: e.target.value})}
                    placeholder="Exemple: Mariages, henna, soirée entre copines..."
                    className="min-h-[60px] sm:min-h-[80px] text-sm sm:text-base"
                  />
                </div>

                <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 pt-2">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => navigate('/mon-espace')}
                    className="flex-1 h-10 sm:h-11 text-sm sm:text-base"
                  >
                    Annuler
                  </Button>
                  <Button type="submit" className="flex-1 h-10 sm:h-11 text-sm sm:text-base bg-orange-600 hover:bg-orange-700">
                    Confirmer la Réservation
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default BookingDetailsPage;