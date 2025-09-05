import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
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
    { name: 'Très simple', price: 5, duration: '10-15 min', description: 'Design sur un doigt' },
    { name: 'Simple', price: 8, duration: '20-30 min', description: 'Design simple sur une main' },
    { name: 'Chargé', price: 12, duration: '45min - 1h', description: 'Design sur les deux mains' },
    { name: 'Mariée', price: 20, duration: '1h - 1h30', description: 'Mains et avant-bras' }
  ];

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

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
      const response = await axios.get(`${API_BASE_URL}/api/slots`);
      const availableSlots = response.data.filter(s => s.is_available);
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

      await axios.post(`${API_BASE_URL}/api/appointments`, {
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
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <Button 
              variant="outline" 
              onClick={() => navigate('/mon-espace')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Finaliser la Réservation
              </h1>
              <p className="text-gray-600">Ajoutez vos informations personnalisées</p>
            </div>
          </div>

          {/* Slot Details Card */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="mr-2 h-5 w-5" />
                Détails du Créneau
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <h3 className="font-semibold text-lg">{slot.service_name}</h3>
                <div className="flex items-center text-gray-600">
                  <Calendar className="mr-2 h-4 w-4" />
                  {formatDate(slot.date)}
                </div>
                <div className="flex items-center text-gray-600">
                  <Clock className="mr-2 h-4 w-4" />
                  {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                </div>
                <p className="text-2xl font-bold text-orange-600">
                  {bookingForm.service_price}€
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Booking Form */}
          <Card>
            <CardHeader>
              <CardTitle>Informations de Réservation</CardTitle>
              <CardDescription>
                Veuillez remplir ces informations pour personnaliser votre rendez-vous
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Service Selection */}
                <div className="space-y-3">
                  <Label className="text-lg font-semibold">🎨 Choisissez votre service</Label>
                  <div className="grid gap-3">
                    {services.map((service) => (
                      <div 
                        key={service.name}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
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
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="font-semibold">{service.name}</h3>
                            <p className="text-sm text-gray-600">{service.description}</p>
                            <p className="text-xs text-gray-500">{service.duration}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xl font-bold text-orange-600">{service.price}€</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="instagram" className="flex items-center">
                    <Instagram className="mr-2 h-4 w-4" />
                    Instagram (optionnel)
                  </Label>
                  <Input
                    id="instagram"
                    value={bookingForm.instagram}
                    onChange={(e) => setBookingForm({...bookingForm, instagram: e.target.value})}
                    placeholder="@votre_instagram"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lieu" className="flex items-center">
                    <MapPin className="mr-2 h-4 w-4" />
                    Lieu souhaité
                  </Label>
                  <Select 
                    value={bookingForm.lieu} 
                    onValueChange={(value) => setBookingForm({...bookingForm, lieu: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choisissez le lieu" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="salon">En salon</SelectItem>
                      <SelectItem value="domicile">À domicile</SelectItem>
                      <SelectItem value="evenement">Événement</SelectItem>
                      <SelectItem value="autre">Autre</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nombre_personnes" className="flex items-center">
                    <Users className="mr-2 h-4 w-4" />
                    Nombre de personnes
                  </Label>
                  <Select 
                    value={bookingForm.nombre_personnes} 
                    onValueChange={(value) => setBookingForm({...bookingForm, nombre_personnes: value})}
                  >
                    <SelectTrigger>
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
                  <Label htmlFor="informations_supplementaires">
                    Informations supplémentaires
                  </Label>
                  <Textarea
                    id="informations_supplementaires"
                    value={bookingForm.informations_supplementaires}
                    onChange={(e) => setBookingForm({...bookingForm, informations_supplementaires: e.target.value})}
                    placeholder="Exemple: Motifs souhaités, allergies, préférences particulières..."
                    className="min-h-[80px]"
                  />
                </div>

                <div className="flex gap-4">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => navigate('/mon-espace')}
                    className="flex-1"
                  >
                    Annuler
                  </Button>
                  <Button type="submit" className="flex-1 bg-orange-600 hover:bg-orange-700">
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