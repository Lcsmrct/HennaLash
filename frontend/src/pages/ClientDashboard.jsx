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

  // Fonction pour parser le lieu depuis les notes
  const parseLieuFromNotes = (notes) => {
    if (!notes) return null;
    
    const lieuMatch = notes.match(/📍 Lieu: (.+?)(?:\n|$)/);
    if (lieuMatch) {
      const lieu = lieuMatch[1].trim();
      // Convertir les valeurs techniques en affichage user-friendly
      switch(lieu) {
        case 'salon': return 'Chez moi';
        case 'domicile': return 'Chez vous';
        case 'evenement': return 'Autre';
        default: return lieu;
      }
    }
    return null;
  };

  // Fonction pour parser l'Instagram depuis les notes
  const parseInstagramFromNotes = (notes) => {
    if (!notes) return null;
    const instagramMatch = notes.match(/📱 Instagram: (.+?)(?:\n|$)/);
    return instagramMatch ? instagramMatch[1].trim() : null;
  };

  // Fonction pour parser le nombre de personnes depuis les notes
  const parsePersonnesFromNotes = (notes) => {
    if (!notes) return null;
    const personnesMatch = notes.match(/👥 Nombre de personnes: (.+?)(?:\n|$)/);
    return personnesMatch ? personnesMatch[1].trim() : null;
  };

  const getStatusBadgeEnhanced = (status) => {
    const statusConfigs = {
      pending: { 
        label: 'En attente', 
        bgColor: 'bg-gradient-to-r from-yellow-50 to-orange-50', 
        textColor: 'text-yellow-800',
        borderColor: 'border-yellow-300',
        icon: '⏳',
        shadowColor: 'shadow-yellow-100'
      },
      confirmed: { 
        label: 'Confirmé', 
        bgColor: 'bg-gradient-to-r from-green-50 to-emerald-50', 
        textColor: 'text-green-800',
        borderColor: 'border-green-300',
        icon: '✅',
        shadowColor: 'shadow-green-100'
      },
      cancelled: { 
        label: 'Annulé', 
        bgColor: 'bg-gradient-to-r from-red-50 to-rose-50', 
        textColor: 'text-red-800',
        borderColor: 'border-red-300',
        icon: '❌',
        shadowColor: 'shadow-red-100'
      },
      completed: { 
        label: 'Terminé', 
        bgColor: 'bg-gradient-to-r from-blue-50 to-indigo-50', 
        textColor: 'text-blue-800',
        borderColor: 'border-blue-300',
        icon: '🎉',
        shadowColor: 'shadow-blue-100'
      }
    };
    
    const config = statusConfigs[status] || statusConfigs.pending;
    return (
      <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold border-2 backdrop-blur-sm ${config.bgColor} ${config.textColor} ${config.borderColor} ${config.shadowColor} shadow-lg transition-all duration-300 hover:scale-105`}>
        <span className="mr-2 text-base">{config.icon}</span>
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
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50 pt-16">
      <Navigation />
      
      <div className="container mx-auto px-3 sm:px-4 py-6 sm:py-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 sm:mb-8 gap-4">
          <div className="w-full sm:w-auto">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-orange-600 via-amber-600 to-rose-600 bg-clip-text text-transparent">
              Bonjour, {user?.first_name} ! ✨
            </h1>
            <p className="text-sm sm:text-base text-gray-600 mt-2 font-medium">Gérez vos rendez-vous et laissez des avis</p>
          </div>
          <Button 
            onClick={logout} 
            variant="outline" 
            className="w-full sm:w-auto min-w-[140px] bg-white/80 backdrop-blur-sm hover:bg-orange-50 border-orange-200 hover:border-orange-300 transition-all duration-300 hover:shadow-lg"
          >
            <LogOut className="mr-2 h-4 w-4" />
            Déconnexion
          </Button>
        </div>

        <Tabs defaultValue="appointments" className="space-y-4 sm:space-y-6">
          <TabsList className="grid w-full grid-cols-3 h-auto p-1 bg-white/80 backdrop-blur-sm border-2 border-orange-100 shadow-lg rounded-xl">
            <TabsTrigger 
              value="appointments" 
              className="text-xs sm:text-sm py-3 px-1 sm:px-3 rounded-lg font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              📅 Mes Rendez-vous
            </TabsTrigger>
            <TabsTrigger 
              value="booking" 
              className="text-xs sm:text-sm py-3 px-1 sm:px-3 rounded-lg font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              🎯 Réserver
            </TabsTrigger>
            <TabsTrigger 
              value="reviews" 
              className="text-xs sm:text-sm py-3 px-1 sm:px-3 rounded-lg font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              ⭐ Laisser un Avis
            </TabsTrigger>
          </TabsList>

          <TabsContent value="appointments" className="space-y-4">
            <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-100 shadow-xl rounded-2xl overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Calendar className="mr-3 h-6 w-6" />
                    <span className="text-xl font-bold">Mes Rendez-vous</span>
                  </div>
                  <Button 
                    variant="secondary" 
                    size="sm" 
                    onClick={fetchData}
                    className="bg-white/20 hover:bg-white/30 text-white border-white/30 backdrop-blur-sm transition-all duration-300"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Actualiser
                  </Button>
                </CardTitle>
                <CardDescription className="text-orange-100 text-base">
                  Consultez vos rendez-vous passés et à venir
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                {appointments.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="mx-auto w-20 h-20 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mb-6 shadow-lg">
                      <Calendar className="w-10 h-10 text-orange-500" />
                    </div>
                    <p className="text-gray-600 text-xl font-semibold mb-3">Aucun rendez-vous</p>
                    <p className="text-gray-500 text-base mb-8 max-w-md mx-auto">Vous n'avez pas encore de rendez-vous programmés. Réservez dès maintenant !</p>
                    <Button 
                      onClick={() => document.querySelector('[value="booking"]').click()} 
                      className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white px-8 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                    >
                      <Calendar className="w-5 h-5 mr-3" />
                      Réserver maintenant
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {appointments.map((appointment) => {
                      const isUpcoming = appointment.status === 'confirmed' || appointment.status === 'pending';
                      const isCompleted = appointment.status === 'completed';
                      const isCancelled = appointment.status === 'cancelled';
                      
                      // Parser les informations depuis les notes
                      const lieu = parseLieuFromNotes(appointment.notes);
                      const instagram = parseInstagramFromNotes(appointment.notes);
                      const personnes = parsePersonnesFromNotes(appointment.notes);
                      
                      return (
                        <div key={appointment.id} className={`border-2 rounded-2xl p-6 transition-all duration-300 hover:shadow-2xl backdrop-blur-sm ${
                          isUpcoming ? 'border-orange-300 bg-gradient-to-br from-orange-50 to-amber-50 hover:from-orange-100 hover:to-amber-100' : 
                          isCompleted ? 'border-green-300 bg-gradient-to-br from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100' :
                          isCancelled ? 'border-red-300 bg-gradient-to-br from-red-50 to-rose-50 hover:from-red-100 hover:to-rose-100' : 'border-gray-300 bg-white/80'
                        }`}>
                          <div className="flex flex-col lg:flex-row gap-6">
                            {/* Service Info */}
                            <div className="flex-1 space-y-4">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <h3 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
                                    <span className="mr-2">🎨</span>
                                    {appointment.service_name || 'Service non spécifié'}
                                  </h3>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-700">
                                    <div className="flex items-center bg-white/60 rounded-lg p-3 shadow-sm">
                                      <Calendar className="w-5 h-5 mr-3 text-orange-500 flex-shrink-0" />
                                      <div>
                                        <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">Date</div>
                                        <div className="font-semibold text-gray-800">
                                          {(appointment.slot_info && appointment.slot_info.date) || appointment.date ? 
                                            formatDate((appointment.slot_info && appointment.slot_info.date) || appointment.date) : 
                                            'Date non spécifiée'}
                                        </div>
                                      </div>
                                    </div>
                                    <div className="flex items-center bg-white/60 rounded-lg p-3 shadow-sm">
                                      <Clock className="w-5 h-5 mr-3 text-orange-500 flex-shrink-0" />
                                      <div>
                                        <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">Heure</div>
                                        <div className="font-semibold text-gray-800">
                                          {(appointment.slot_info && appointment.slot_info.start_time) || appointment.start_time ? 
                                            `${formatTime((appointment.slot_info && appointment.slot_info.start_time) || appointment.start_time)}` : 
                                            'Heure non spécifiée'}
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Status et Prix */}
                                <div className="flex flex-col items-end gap-3 ml-4">
                                  {getStatusBadgeEnhanced(appointment.status)}
                                  <div className="bg-gradient-to-r from-orange-500 to-amber-500 text-white px-4 py-2 rounded-xl font-bold text-lg shadow-lg">
                                    {appointment.service_price || 0}€
                                  </div>
                                </div>
                              </div>

                              {/* Informations détaillées */}
                              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                {lieu && (
                                  <div className="bg-white/80 rounded-xl p-3 border border-orange-200 shadow-sm">
                                    <div className="flex items-center">
                                      <div className="w-8 h-8 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mr-3">
                                        <span className="text-sm">📍</span>
                                      </div>
                                      <div>
                                        <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">Lieu</div>
                                        <div className="font-semibold text-gray-800">{lieu}</div>
                                      </div>
                                    </div>
                                  </div>
                                )}
                                
                                {personnes && (
                                  <div className="bg-white/80 rounded-xl p-3 border border-orange-200 shadow-sm">
                                    <div className="flex items-center">
                                      <div className="w-8 h-8 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mr-3">
                                        <span className="text-sm">👥</span>
                                      </div>
                                      <div>
                                        <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">Personnes</div>
                                        <div className="font-semibold text-gray-800">{personnes}</div>
                                      </div>
                                    </div>
                                  </div>
                                )}

                                {instagram && (
                                  <div className="bg-white/80 rounded-xl p-3 border border-orange-200 shadow-sm">
                                    <div className="flex items-center">
                                      <div className="w-8 h-8 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mr-3">
                                        <span className="text-sm">📱</span>
                                      </div>
                                      <div>
                                        <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">Instagram</div>
                                        <div className="font-semibold text-gray-800">{instagram}</div>
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Notes supplémentaires */}
                              {appointment.notes && appointment.notes.includes('ℹ️ Informations supplémentaires:') && (
                                <div className="bg-white/80 rounded-xl p-4 border border-orange-200 shadow-sm">
                                  <div className="flex items-start">
                                    <MessageSquare className="w-5 h-5 mr-3 flex-shrink-0 mt-1 text-orange-500" />
                                    <div>
                                      <div className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-1">Notes</div>
                                      <div className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                                        {appointment.notes.split('ℹ️ Informations supplémentaires:\n')[1] || 'Aucune note supplémentaire'}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Actions pour les RDV à venir */}
                              {isUpcoming && (
                                <div className="flex justify-center pt-2">
                                  <div className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-800 border-2 border-blue-200 shadow-sm">
                                    <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                    </svg>
                                    {appointment.status === 'pending' ? 'En attente de confirmation' : 'Confirmé - À venir'}
                                  </div>
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
            <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-100 shadow-xl rounded-2xl overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                <CardTitle className="flex items-center">
                  <Calendar className="mr-3 h-6 w-6" />
                  <span className="text-xl font-bold">Réserver un Rendez-vous</span>
                </CardTitle>
                <CardDescription className="text-orange-100 text-base">
                  Choisissez parmi les créneaux disponibles et sélectionnez votre service
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                {availableSlots.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="mx-auto w-20 h-20 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mb-6 shadow-lg">
                      <Clock className="w-10 h-10 text-orange-500" />
                    </div>
                    <p className="text-gray-600 text-xl font-semibold mb-3">Aucun créneau disponible</p>
                    <p className="text-gray-500 text-base mb-8 max-w-md mx-auto">Les créneaux sont mis à jour régulièrement. Revenez bientôt !</p>
                    <Button 
                      variant="outline" 
                      onClick={fetchData}
                      className="bg-white/80 hover:bg-orange-50 border-orange-200 hover:border-orange-300 transition-all duration-300 px-8 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl"
                    >
                      <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Vérifier les disponibilités
                    </Button>
                  </div>
                ) : (
                  <div>
                    <div className="mb-8 p-6 bg-gradient-to-r from-orange-50 to-amber-50 rounded-2xl border-2 border-orange-200 shadow-lg">
                      <h3 className="font-bold text-orange-800 mb-4 text-lg flex items-center">
                        <span className="mr-2">🎨</span>
                        Nos Services Premium
                      </h3>
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="text-center bg-white/70 rounded-xl p-3 border border-orange-200 shadow-sm hover:shadow-md transition-all duration-300">
                          <div className="w-12 h-12 bg-gradient-to-br from-orange-200 to-amber-200 rounded-full flex items-center justify-center mx-auto mb-2">
                            <span className="text-lg">✨</span>
                          </div>
                          <div className="font-semibold text-orange-700 text-sm">Très simple</div>
                          <div className="text-orange-600 font-bold">5€ par main</div>
                        </div>
                        <div className="text-center bg-white/70 rounded-xl p-3 border border-orange-200 shadow-sm hover:shadow-md transition-all duration-300">
                          <div className="w-12 h-12 bg-gradient-to-br from-orange-300 to-amber-300 rounded-full flex items-center justify-center mx-auto mb-2">
                            <span className="text-lg">🌟</span>
                          </div>
                          <div className="font-semibold text-orange-700 text-sm">Simple</div>
                          <div className="text-orange-600 font-bold">8€ par main</div>
                        </div>
                        <div className="text-center bg-white/70 rounded-xl p-3 border border-orange-200 shadow-sm hover:shadow-md transition-all duration-300">
                          <div className="w-12 h-12 bg-gradient-to-br from-orange-400 to-amber-400 rounded-full flex items-center justify-center mx-auto mb-2">
                            <span className="text-lg">💫</span>
                          </div>
                          <div className="font-semibold text-orange-700 text-sm">Chargé</div>
                          <div className="text-orange-600 font-bold">12€ par mains</div>
                        </div>
                        <div className="text-center bg-white/70 rounded-xl p-3 border border-orange-200 shadow-sm hover:shadow-md transition-all duration-300">
                          <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-amber-500 rounded-full flex items-center justify-center mx-auto mb-2">
                            <span className="text-lg">👰</span>
                          </div>
                          <div className="font-semibold text-orange-700 text-sm">Mariée</div>
                          <div className="text-orange-600 font-bold">20€ complet</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid gap-6 grid-cols-1 md:grid-cols-2 xl:grid-cols-3">
                      {availableSlots.map((slot, index) => {
                        console.log(`Slot ${index}:`, slot); // Debug chaque slot
                        const slotDate = new Date(slot.date);
                        const isToday = slotDate.toDateString() === new Date().toDateString();
                        const isTomorrow = slotDate.toDateString() === new Date(Date.now() + 86400000).toDateString();
                        
                        return (
                          <Card key={slot.id} className="cursor-pointer hover:shadow-2xl transition-all duration-300 border-2 hover:border-orange-400 h-full group bg-white/80 backdrop-blur-sm rounded-2xl overflow-hidden transform hover:scale-105">
                            <CardContent className="p-6 h-full flex flex-col">
                              <div className="flex justify-between items-start mb-4">
                                <div className="flex-1">
                                  <h3 className="font-bold text-xl text-gray-900 mb-2 group-hover:text-orange-600 transition-colors flex items-center">
                                    {isToday ? (
                                      <>
                                        <span className="mr-2">🔥</span>
                                        <span className="bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">Aujourd'hui</span>
                                      </>
                                    ) : isTomorrow ? (
                                      <>
                                        <span className="mr-2">⚡</span>
                                        <span className="bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">Demain</span>
                                      </>
                                    ) : (
                                      <>
                                        <span className="mr-2">✨</span>
                                        <span>Disponible</span>
                                      </>
                                    )}
                                  </h3>
                                </div>
                                <div className="bg-gradient-to-r from-green-400 to-emerald-400 text-white text-xs px-3 py-2 rounded-full font-semibold shadow-md">
                                  Libre
                                </div>
                              </div>
                              
                              <div className="space-y-4 text-sm flex-1">
                                <div className="flex items-center bg-gradient-to-r from-gray-50 to-orange-50 rounded-xl p-4 shadow-sm border border-orange-100">
                                  <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-amber-400 rounded-full flex items-center justify-center mr-4">
                                    <Calendar className="w-5 h-5 text-white" />
                                  </div>
                                  <div>
                                    <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">Date</div>
                                    <div className="font-bold text-gray-800">
                                      {slot.date ? formatDate(slot.date) : 'Date non spécifiée'}
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center bg-gradient-to-r from-gray-50 to-orange-50 rounded-xl p-4 shadow-sm border border-orange-100">
                                  <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-amber-400 rounded-full flex items-center justify-center mr-4">
                                    <Clock className="w-5 h-5 text-white" />
                                  </div>
                                  <div>
                                    <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">Horaire</div>
                                    <div className="font-bold text-gray-800">
                                      {slot.start_time ? `${formatTime(slot.start_time)} - ${slot.end_time ? formatTime(slot.end_time) : '(+1h)'}` : 'Heure non spécifiée'}
                                    </div>
                                  </div>
                                </div>
                                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border-2 border-blue-200">
                                  <p className="text-sm text-blue-700 font-semibold flex items-center">
                                    <span className="mr-2">✨</span>
                                    Choisissez votre service lors de la réservation
                                  </p>
                                </div>
                              </div>
                              
                              <Button 
                                className="w-full mt-6 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold py-3 transition-all duration-300 group-hover:shadow-xl transform group-hover:scale-105 rounded-xl" 
                                onClick={() => goToBookingDetails(slot.id)}
                              >
                                <Calendar className="w-5 h-5 mr-3" />
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
            <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-100 shadow-xl rounded-2xl overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                <CardTitle className="flex items-center">
                  <Star className="mr-3 h-6 w-6" />
                  <span className="text-xl font-bold">Laisser un Avis</span>
                </CardTitle>
                <CardDescription className="text-orange-100 text-base">
                  Partagez votre expérience avec nous
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <form onSubmit={submitReview} className="space-y-8">
                  <div className="space-y-4">
                    <Label className="text-lg font-semibold text-gray-800 flex items-center">
                      <span className="mr-2">⭐</span>
                      Votre note
                    </Label>
                    <Select 
                      value={reviewForm.rating.toString()} 
                      onValueChange={(value) => setReviewForm({...reviewForm, rating: parseInt(value)})}
                    >
                      <SelectTrigger className="w-full h-14 text-base bg-white/90 border-2 border-orange-200 rounded-xl hover:border-orange-300 transition-all duration-300 shadow-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-white/95 backdrop-blur-sm border-2 border-orange-200 rounded-xl shadow-xl">
                        <SelectItem value="5" className="text-base py-3 hover:bg-orange-50">
                          <div className="flex items-center">
                            <span className="mr-3 text-xl">⭐⭐⭐⭐⭐</span>
                            <span className="font-semibold">Excellent (5/5)</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="4" className="text-base py-3 hover:bg-orange-50">
                          <div className="flex items-center">
                            <span className="mr-3 text-xl">⭐⭐⭐⭐</span>
                            <span className="font-semibold">Très bien (4/5)</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="3" className="text-base py-3 hover:bg-orange-50">
                          <div className="flex items-center">
                            <span className="mr-3 text-xl">⭐⭐⭐</span>
                            <span className="font-semibold">Bien (3/5)</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="2" className="text-base py-3 hover:bg-orange-50">
                          <div className="flex items-center">
                            <span className="mr-3 text-xl">⭐⭐</span>
                            <span className="font-semibold">Moyen (2/5)</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="1" className="text-base py-3 hover:bg-orange-50">
                          <div className="flex items-center">
                            <span className="mr-3 text-xl">⭐</span>
                            <span className="font-semibold">Décevant (1/5)</span>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-4">
                    <Label htmlFor="comment" className="text-lg font-semibold text-gray-800 flex items-center">
                      <span className="mr-2">💬</span>
                      Votre commentaire
                    </Label>
                    <Textarea
                      id="comment"
                      value={reviewForm.comment}
                      onChange={(e) => setReviewForm({...reviewForm, comment: e.target.value})}
                      placeholder="Partagez votre expérience avec nous... Qu'avez-vous pensé du service ? Y a-t-il quelque chose que vous aimeriez améliorer ?"
                      className="min-h-[120px] text-base bg-white/90 border-2 border-orange-200 rounded-xl hover:border-orange-300 focus:border-orange-400 transition-all duration-300 shadow-sm resize-none"
                      required
                    />
                    <p className="text-sm text-gray-500 italic">
                      💡 Votre avis nous aide à améliorer nos services et aide d'autres clients à faire leur choix
                    </p>
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full py-4 text-lg font-bold bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                  >
                    <Star className="w-5 h-5 mr-3" />
                    Soumettre mon avis
                  </Button>
                  
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border-2 border-blue-200">
                    <p className="text-sm text-blue-700 font-medium flex items-center">
                      <span className="mr-2">ℹ️</span>
                      Votre avis sera examiné par notre équipe avant publication pour maintenir la qualité de nos services
                    </p>
                  </div>
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