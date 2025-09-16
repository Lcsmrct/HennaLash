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

  const getStatusBadgeEnhanced = (status) => {
    const statusConfigs = {
      pending: { 
        label: 'En attente', 
        bgColor: 'bg-yellow-100', 
        textColor: 'text-yellow-800',
        borderColor: 'border-yellow-200',
        icon: '⏳'
      },
      confirmed: { 
        label: 'Confirmé', 
        bgColor: 'bg-green-100', 
        textColor: 'text-green-800',
        borderColor: 'border-green-200',
        icon: '✅'
      },
      cancelled: { 
        label: 'Annulé', 
        bgColor: 'bg-red-100', 
        textColor: 'text-red-800',
        borderColor: 'border-red-200',
        icon: '❌'
      },
      completed: { 
        label: 'Terminé', 
        bgColor: 'bg-blue-100', 
        textColor: 'text-blue-800',
        borderColor: 'border-blue-200',
        icon: '🎉'
      }
    };
    
    const config = statusConfigs[status] || statusConfigs.pending;
    return (
      <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${config.bgColor} ${config.textColor} ${config.borderColor}`}>
        <span className="mr-1">{config.icon}</span>
        {config.label}
      </div>
    );
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
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Calendar className="mr-2 h-5 w-5" />
                    Mes Rendez-vous
                  </div>
                  <Button variant="outline" size="sm" onClick={fetchData}>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Actualiser
                  </Button>
                </CardTitle>
                <CardDescription>
                  Consultez vos rendez-vous passés et à venir
                </CardDescription>
              </CardHeader>
              <CardContent>
                {appointments.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                      <Calendar className="w-8 h-8 text-gray-400" />
                    </div>
                    <p className="text-gray-500 text-lg font-medium mb-2">Aucun rendez-vous</p>
                    <p className="text-gray-400 text-sm mb-6">Vous n'avez pas encore de rendez-vous programmés</p>
                    <Button onClick={() => document.querySelector('[value="booking"]').click()} className="bg-orange-600 hover:bg-orange-700">
                      <Calendar className="w-4 h-4 mr-2" />
                      Réserver maintenant
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {appointments.map((appointment) => {
                      const isUpcoming = appointment.status === 'confirmed' || appointment.status === 'pending';
                      const isCompleted = appointment.status === 'completed';
                      const isCancelled = appointment.status === 'cancelled';
                      
                      return (
                        <div key={appointment.id} className={`border-2 rounded-xl p-4 sm:p-6 transition-all hover:shadow-lg ${
                          isUpcoming ? 'border-orange-200 bg-orange-50/50' : 
                          isCompleted ? 'border-green-200 bg-green-50/50' :
                          isCancelled ? 'border-red-200 bg-red-50/50' : 'border-gray-200 bg-white'
                        }`}>
                          <div className="flex flex-col lg:flex-row gap-4">
                            {/* Service Info */}
                            <div className="flex-1 space-y-3">
                              <div className="flex items-start justify-between">
                                <div>
                                  <h3 className="text-lg font-bold text-gray-900 mb-1">
                                    {appointment.service_name || 'Service non spécifié'}
                                  </h3>
                                  <div className="flex items-center gap-4 text-sm text-gray-600">
                                    <div className="flex items-center">
                                      <Calendar className="w-4 h-4 mr-1 flex-shrink-0" />
                                      <span className="font-medium">
                                        {(appointment.slot_info && appointment.slot_info.date) || appointment.date ? 
                                          formatDate((appointment.slot_info && appointment.slot_info.date) || appointment.date) : 
                                          'Date non spécifiée'}
                                      </span>
                                    </div>
                                    <div className="flex items-center">
                                      <Clock className="w-4 h-4 mr-1 flex-shrink-0" />
                                      <span className="font-medium">
                                        {(appointment.slot_info && appointment.slot_info.start_time) || appointment.start_time ? 
                                          `${formatTime((appointment.slot_info && appointment.slot_info.start_time) || appointment.start_time)}` : 
                                          'Heure non spécifiée'}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Status et Prix */}
                                <div className="flex flex-col items-end gap-2">
                                  {getStatusBadgeEnhanced(appointment.status)}
                                  <div className="text-2xl font-bold text-orange-600">
                                    {appointment.service_price || 0}€
                                  </div>
                                </div>
                              </div>

                              {/* Notes/Détails */}
                              {appointment.notes && (
                                <div className="bg-white/80 rounded-lg p-3 border border-gray-100">
                                  <div className="flex items-start">
                                    <MessageSquare className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5 text-gray-500" />
                                    <div className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                                      {appointment.notes}
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Actions pour les RDV à venir */}
                              {isUpcoming && (
                                <div className="flex flex-wrap gap-2 pt-2">
                                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                    </svg>
                                    {appointment.status === 'pending' ? 'En attente de confirmation' : 'Confirmé - À venir'}
                                  </span>
                                </div>
                              )}
                            </div>
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
                  Choisissez parmi les créneaux disponibles et sélectionnez votre service
                </CardDescription>
              </CardHeader>
              <CardContent>
                {availableSlots.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="mx-auto w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
                      <Clock className="w-8 h-8 text-orange-500" />
                    </div>
                    <p className="text-gray-500 text-lg font-medium mb-2">Aucun créneau disponible</p>
                    <p className="text-gray-400 text-sm mb-6">Les créneaux sont mis à jour régulièrement</p>
                    <Button variant="outline" onClick={fetchData}>
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Vérifier les disponibilités
                    </Button>
                  </div>
                ) : (
                  <div>
                    <div className="mb-6 p-4 bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg border border-orange-200">
                      <h3 className="font-semibold text-orange-800 mb-2">🎨 Nos Services</h3>
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 text-xs">
                        <div className="text-center">
                          <div className="font-medium text-orange-700">Très simple</div>
                          <div className="text-orange-600">5€ par main</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-orange-700">Simple</div>
                          <div className="text-orange-600">8€ par main</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-orange-700">Chargé</div>
                          <div className="text-orange-600">12€ par mains</div>
                        </div>
                        <div className="text-center">
                          <div className="font-medium text-orange-700">Mariée</div>
                          <div className="text-orange-600">20€ complet</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-3">
                      {availableSlots.map((slot, index) => {
                        console.log(`Slot ${index}:`, slot); // Debug chaque slot
                        const slotDate = new Date(slot.date);
                        const isToday = slotDate.toDateString() === new Date().toDateString();
                        const isTomorrow = slotDate.toDateString() === new Date(Date.now() + 86400000).toDateString();
                        
                        return (
                          <Card key={slot.id} className="cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-orange-300 h-full group">
                            <CardContent className="p-4 h-full flex flex-col">
                              <div className="flex justify-between items-start mb-3">
                                <div className="flex-1">
                                  <h3 className="font-bold text-lg text-gray-900 mb-1 group-hover:text-orange-600 transition-colors">
                                    {isToday ? '🔥 Aujourd\'hui' : isTomorrow ? '⚡ Demain' : 'Disponible'}
                                  </h3>
                                </div>
                                <div className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full font-medium">
                                  Libre
                                </div>
                              </div>
                              
                              <div className="space-y-3 text-sm flex-1">
                                <div className="flex items-center bg-gray-50 rounded-lg p-2">
                                  <Calendar className="w-4 h-4 mr-2 text-orange-500 flex-shrink-0" />
                                  <span className="font-medium text-gray-700">
                                    {slot.date ? formatDate(slot.date) : 'Date non spécifiée'}
                                  </span>
                                </div>
                                <div className="flex items-center bg-gray-50 rounded-lg p-2">
                                  <Clock className="w-4 h-4 mr-2 text-orange-500 flex-shrink-0" />
                                  <span className="font-medium text-gray-700">
                                    {slot.start_time ? `${formatTime(slot.start_time)} - ${slot.end_time ? formatTime(slot.end_time) : '(+1h)'}` : 'Heure non spécifiée'}
                                  </span>
                                </div>
                                <div className="bg-blue-50 rounded-lg p-2">
                                  <p className="text-xs text-blue-600 font-medium">
                                    ✨ Choisissez votre service lors de la réservation
                                  </p>
                                </div>
                              </div>
                              
                              <Button 
                                className="w-full mt-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium transition-all duration-200 group-hover:shadow-md" 
                                onClick={() => goToBookingDetails(slot.id)}
                              >
                                <Calendar className="w-4 h-4 mr-2" />
                                Réserver ce créneau
                              </Button>
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
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
                <form onSubmit={submitReview} className="space-y-4 sm:space-y-6">
                  <div className="space-y-2">
                    <Label className="text-sm sm:text-base">Note</Label>
                    <Select 
                      value={reviewForm.rating.toString()} 
                      onValueChange={(value) => setReviewForm({...reviewForm, rating: parseInt(value)})}
                    >
                      <SelectTrigger className="w-full h-10 sm:h-11">
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
                    <Label htmlFor="comment" className="text-sm sm:text-base">Commentaire</Label>
                    <Textarea
                      id="comment"
                      value={reviewForm.comment}
                      onChange={(e) => setReviewForm({...reviewForm, comment: e.target.value})}
                      placeholder="Partagez votre expérience..."
                      className="min-h-[80px] sm:min-h-[100px] text-sm sm:text-base"
                      required
                    />
                  </div>
                  
                  <Button type="submit" className="w-full py-2 sm:py-3 text-sm sm:text-base font-medium">
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