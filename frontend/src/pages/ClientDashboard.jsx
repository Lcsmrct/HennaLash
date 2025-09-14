import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, useNavigate } from 'react-router-dom';
import apiService from '../services/apiService';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Calendar, Clock, Star, User, LogOut, MessageSquare } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from '../hooks/use-toast';
import Navigation from '../components/Navigation';

const ClientDashboard = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  // États locaux au lieu du hook useCache pour éviter les erreurs d'ordre des hooks
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [appointments, setAppointments] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });

  // Fonction pour charger les données
  const loadDashboardData = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      const data = await apiService.getDashboardData('client');
      console.log('Dashboard data received:', data);
      console.log('Available slots:', data?.slots);
      setDashboardData(data);
      setAppointments(data?.appointments || []);
      setAvailableSlots(data?.slots || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  // Effet pour charger les données au montage
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Redirect if not authenticated or is admin - APRÈS tous les hooks
  if (!isAuthenticated) {
    return <Navigate to="/connexion" replace />;
  }

  if (user?.role === 'admin') {
    return <Navigate to="/admin" replace />;
  }

  const fetchData = async () => {
    try {
      await loadDashboardData();
      toast({
        title: "Succès",
        description: "Données actualisées",
      });
    } catch (error) {
      console.error('Error fetching data:', error);
      toast({
        title: "Erreur",
        description: "Impossible de charger les données",
        variant: "destructive"
      });
    }
  };

  const goToBookingDetails = (slotId) => {
    navigate(`/reserver/${slotId}`);
  };

  const submitReview = async (e) => {
    e.preventDefault();
    try {
      await apiService.createReview(reviewForm);
      
      toast({
        title: "Succès",
        description: "Votre avis a été soumis et sera examiné par l'équipe !"
      });
      
      setReviewForm({ rating: 5, comment: '' });
    } catch (error) {
      console.error('Error submitting review:', error);
      toast({
        title: "Erreur",
        description: "Impossible de soumettre votre avis",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      pending: { label: 'En attente', variant: 'secondary' },
      confirmed: { label: 'Confirmé', variant: 'default' },
      cancelled: { label: 'Annulé', variant: 'destructive' },
      completed: { label: 'Terminé', variant: 'success' }
    };
    
    const statusInfo = statusMap[status] || { label: status, variant: 'secondary' };
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>;
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

  return (
    <div className="min-h-screen bg-gray-50 pt-16">
      <Navigation />
      
      <div className="container mx-auto px-3 sm:px-4 py-6 sm:py-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 sm:mb-8 gap-4">
          <div className="w-full sm:w-auto">
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">
              Bonjour, {user?.first_name} !
            </h1>
            <p className="text-sm sm:text-base text-gray-600 mt-1">Gérez vos rendez-vous et laissez des avis</p>
          </div>
          <Button onClick={logout} variant="outline" className="w-full sm:w-auto min-w-[120px]">
            <LogOut className="mr-2 h-4 w-4" />
            Déconnexion
          </Button>
        </div>

        <Tabs defaultValue="appointments" className="space-y-4 sm:space-y-6">
          <TabsList className="grid w-full grid-cols-3 h-auto p-1">
            <TabsTrigger value="appointments" className="text-xs sm:text-sm py-2 px-1 sm:px-3">
              Mes Rendez-vous
            </TabsTrigger>
            <TabsTrigger value="booking" className="text-xs sm:text-sm py-2 px-1 sm:px-3">
              Réserver
            </TabsTrigger>
            <TabsTrigger value="reviews" className="text-xs sm:text-sm py-2 px-1 sm:px-3">
              Laisser un Avis
            </TabsTrigger>
          </TabsList>

          <TabsContent value="appointments" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="mr-2 h-5 w-5" />
                  Mes Rendez-vous
                </CardTitle>
                <CardDescription>
                  Consultez vos rendez-vous passés et à venir
                </CardDescription>
              </CardHeader>
              <CardContent>
                {appointments.length === 0 ? (
                  <p className="text-center text-gray-500 py-6 sm:py-8 text-sm sm:text-base">
                    Aucun rendez-vous pour le moment
                  </p>
                ) : (
                  <div className="space-y-3 sm:space-y-4">
                    {appointments.map((appointment) => {
                      console.log('Appointment data:', appointment); // Debug temporaire
                      return (
                        <div key={appointment.id} className="border rounded-lg p-3 sm:p-4 bg-white">
                          <div className="flex flex-col gap-3 sm:gap-4">
                            <div className="flex flex-col sm:flex-row justify-between items-start gap-3 sm:gap-4">
                              <div className="space-y-2 flex-1 min-w-0">
                                <h3 className="font-semibold text-sm sm:text-base leading-tight">
                                  {appointment.service_name || 'Service non spécifié'}
                                </h3>
                                <div className="flex items-center text-xs sm:text-sm text-gray-600">
                                  <Calendar className="mr-1 h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
                                  <span className="truncate">
                                    {appointment.slot_info && appointment.slot_info.date ? 
                                      formatDate(appointment.slot_info.date) : 
                                      'Date non spécifiée'}
                                  </span>
                                </div>
                                <div className="flex items-center text-xs sm:text-sm text-gray-600">
                                  <Clock className="mr-1 h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
                                  <span>
                                    {appointment.slot_info && appointment.slot_info.start_time ? 
                                      `${formatTime(appointment.slot_info.start_time)}` : 
                                      'Heure non spécifiée'}
                                  </span>
                                </div>
                              </div>
                              <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between sm:justify-start gap-2 sm:gap-2 w-full sm:w-auto">
                                {getStatusBadge(appointment.status)}
                                <p className="text-base sm:text-lg font-semibold">
                                  {appointment.service_price || 0}€
                                </p>
                              </div>
                            </div>
                            {appointment.notes && (
                              <div className="pt-2 border-t border-gray-100">
                                <p className="text-xs sm:text-sm text-gray-600 flex items-start">
                                  <MessageSquare className="mr-1 h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0 mt-0.5" />
                                  <span className="break-words">{appointment.notes}</span>
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="booking" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="mr-2 h-5 w-5" />
                  Réserver un Rendez-vous
                </CardTitle>
                <CardDescription>
                  Choisissez parmi les créneaux disponibles
                </CardDescription>
              </CardHeader>
              <CardContent>
                {availableSlots.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">
                    Aucun créneau disponible pour le moment
                  </p>
                ) : (
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {availableSlots.map((slot, index) => {
                      console.log(`Slot ${index}:`, slot); // Debug chaque slot
                      return (
                        <Card key={slot.id} className="cursor-pointer hover:shadow-md transition-shadow">
                          <CardContent className="p-4">
                            <h3 className="font-semibold mb-2">Créneau Disponible</h3>
                            <div className="space-y-2 text-sm text-gray-600">
                              <div className="flex items-center">
                                <Calendar className="mr-1 h-4 w-4" />
                                {slot.date ? formatDate(slot.date) : 'Date non spécifiée'}
                              </div>
                              <div className="flex items-center">
                                <Clock className="mr-1 h-4 w-4" />
                                {slot.start_time ? formatTime(slot.start_time) : 'Heure non spécifiée'}
                              </div>
                              <p className="text-sm text-gray-500">
                                Service à choisir lors de la réservation
                              </p>
                            </div>
                            <Button 
                              className="w-full mt-4 py-3" 
                              onClick={() => goToBookingDetails(slot.id)}
                            >
                              Réserver ce créneau
                            </Button>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reviews">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Star className="mr-2 h-5 w-5" />
                  Laisser un Avis
                </CardTitle>
                <CardDescription>
                  Partagez votre expérience avec nous
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={submitReview} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Note</Label>
                    <Select 
                      value={reviewForm.rating.toString()} 
                      onValueChange={(value) => setReviewForm({...reviewForm, rating: parseInt(value)})}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="5">⭐⭐⭐⭐⭐ (5/5)</SelectItem>
                        <SelectItem value="4">⭐⭐⭐⭐ (4/5)</SelectItem>
                        <SelectItem value="3">⭐⭐⭐ (3/5)</SelectItem>
                        <SelectItem value="2">⭐⭐ (2/5)</SelectItem>
                        <SelectItem value="1">⭐ (1/5)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="comment">Commentaire</Label>
                    <Textarea
                      id="comment"
                      value={reviewForm.comment}
                      onChange={(e) => setReviewForm({...reviewForm, comment: e.target.value})}
                      placeholder="Partagez votre expérience..."
                      className="min-h-[100px]"
                      required
                    />
                  </div>
                  
                  <Button type="submit" className="w-full py-3">
                    Soumettre l'avis
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ClientDashboard;