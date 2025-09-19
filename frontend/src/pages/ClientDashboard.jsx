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

  const deleteAppointment = async (appointmentId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce rendez-vous de votre historique ?')) {
      return;
    }
    
    try {
      await apiService.deleteAppointment(appointmentId);
      setAppointments(appointments.filter(app => app.id !== appointmentId));
      toast({
        title: "Succès",
        description: "Rendez-vous supprimé de votre historique"
      });
    } catch (error) {
      console.error('Error deleting appointment:', error);
      toast({
        title: "Erreur", 
        description: error.response?.data?.detail || "Impossible de supprimer le rendez-vous",
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

  // Fonction pour parser les informations supplémentaires depuis les notes
  const parseInformationsSupplementairesFromNotes = (notes) => {
    if (!notes) return null;
    const infoMatch = notes.match(/ℹ️ Informations supplémentaires:\s*\n(.+?)(?=\n\n|$)/s);
    return infoMatch ? infoMatch[1].trim() : null;
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
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50">
      <Navigation />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
        {/* Header amélioré avec meilleure visibilité */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-6">
          <div className="w-full sm:w-auto">
            {/* Titre principal avec fond semi-transparent pour meilleure lisibilité */}
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-xl border-2 border-orange-200">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-3">
                <span className="bg-gradient-to-r from-orange-600 via-amber-600 to-rose-600 bg-clip-text text-transparent">
                  Bonjour, {user?.first_name} ! ✨
                </span>
              </h1>
              <p className="text-lg sm:text-xl text-gray-700 font-semibold">
                Gérez vos rendez-vous et laissez des avis
              </p>
              <div className="mt-3 flex items-center text-sm text-gray-600">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                Connecté en tant que client
              </div>
            </div>
          </div>
          <div className="w-full sm:w-auto">
            <Button 
              onClick={logout} 
              variant="outline" 
              size="lg"
              className="w-full sm:w-auto min-w-[160px] bg-white/90 backdrop-blur-sm hover:bg-orange-50 border-2 border-orange-300 hover:border-orange-400 transition-all duration-300 hover:shadow-xl text-gray-700 font-semibold"
            >
              <LogOut className="mr-2 h-5 w-5" />
              Déconnexion
            </Button>
          </div>
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
                    {appointments.filter((appointment) => {
                      // Masquer les RDV passés de plus de 24h
                      if (appointment.status === 'completed' || appointment.status === 'cancelled') {
                        const appointmentDate = new Date(
                          (appointment.slot_info && appointment.slot_info.date) || appointment.date || new Date()
                        );
                        const now = new Date();
                        const hoursDiff = (now - appointmentDate) / (1000 * 60 * 60);
                        
                        // Masquer si passé depuis plus de 24h
                        if (hoursDiff > 24) {
                          return false;
                        }
                      }
                      return true;
                    }).map((appointment) => {
                      const isUpcoming = appointment.status === 'confirmed' || appointment.status === 'pending';
                      const isCompleted = appointment.status === 'completed';
                      const isCancelled = appointment.status === 'cancelled';
                      
                      // Vérifier si le RDV est passé (pour le bouton supprimer)
                      const appointmentDate = new Date(
                        (appointment.slot_info && appointment.slot_info.date) || appointment.date || new Date()
                      );
                      const now = new Date();
                      const isPastAppointment = appointmentDate < now;
                      
                      // Parser les informations depuis les notes
                      const lieu = parseLieuFromNotes(appointment.notes);
                      const instagram = parseInstagramFromNotes(appointment.notes);
                      const personnes = parsePersonnesFromNotes(appointment.notes);
                      const informationsSupplementaires = parseInformationsSupplementairesFromNotes(appointment.notes);
                      
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
                                {informationsSupplementaires && (
                                  <div className="bg-white/80 rounded-xl p-3 border border-orange-200 shadow-sm">
                                    <div className="flex items-start">
                                      <div className="w-8 h-8 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0 mt-0.5">
                                        <span className="text-sm">💬</span>
                                      </div>
                                      <div>
                                        <div className="text-xs text-gray-500 uppercase tracking-wide font-medium">Notes supplémentaires</div>
                                        <div className="font-semibold text-gray-800 text-sm whitespace-pre-line">{informationsSupplementaires}</div>
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </div>

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
                              
                              {/* Bouton Supprimer pour les RDV passés */}
                              {isPastAppointment && (isCompleted || isCancelled) && (
                                <div className="flex justify-center pt-4">
                                  <Button 
                                    variant="outline"
                                    size="sm"
                                    onClick={() => deleteAppointment(appointment.id)}
                                    className="border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 transition-all duration-300"
                                  >
                                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                    Supprimer
                                  </Button>
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
            <Card className="bg-white/95 backdrop-blur-sm border-2 border-orange-100 shadow-xl rounded-2xl overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                <CardTitle className="flex items-center">
                  <Calendar className="mr-3 h-6 w-6" />
                  <span className="text-xl font-bold drop-shadow-sm">Réserver un Rendez-vous</span>
                </CardTitle>
                <CardDescription className="text-orange-50 text-base font-medium drop-shadow-sm">
                  Choisissez parmi les créneaux disponibles et sélectionnez votre service
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                {availableSlots.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="mx-auto w-20 h-20 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mb-6 shadow-lg">
                      <Clock className="w-10 h-10 text-orange-500" />
                    </div>
                    <p className="text-gray-700 text-xl font-semibold mb-3">Aucun créneau disponible</p>
                    <p className="text-gray-600 text-base mb-8 max-w-md mx-auto">Les créneaux sont mis à jour régulièrement. Revenez bientôt !</p>
                    <Button 
                      variant="outline" 
                      onClick={fetchData}
                      className="bg-white hover:bg-orange-50 border-orange-200 hover:border-orange-400 transition-all duration-300 px-8 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl"
                    >
                      <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Vérifier les disponibilités
                    </Button>
                  </div>
                ) : (
                  <div>
                    {/* Services Info - Version simple et pro avec meilleure lisibilité */}
                    <div className="mb-8">
                      <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-6 border-2 border-orange-200 shadow-lg">
                        <h3 className="font-bold text-gray-800 mb-4 flex items-center text-lg">
                          <span className="mr-3 text-2xl" role="img" aria-label="palette">🎨</span>
                          <span className="text-gray-800">Nos Services & Tarifs</span>
                        </h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                          <div className="text-center p-4 bg-white rounded-xl shadow-sm border-2 border-orange-100 hover:shadow-md transition-all duration-200">
                            <div className="text-sm font-bold text-gray-700 mb-1">Très simple</div>
                            <div className="text-xl font-black text-orange-600">5€</div>
                            <div className="text-xs text-gray-500 mt-1">Design basique</div>
                          </div>
                          <div className="text-center p-4 bg-white rounded-xl shadow-sm border-2 border-orange-100 hover:shadow-md transition-all duration-200">
                            <div className="text-sm font-bold text-gray-700 mb-1">Simple</div>
                            <div className="text-xl font-black text-orange-600">8€</div>
                            <div className="text-xs text-gray-500 mt-1">Design élégant</div>
                          </div>
                          <div className="text-center p-4 bg-white rounded-xl shadow-sm border-2 border-orange-100 hover:shadow-md transition-all duration-200">
                            <div className="text-sm font-bold text-gray-700 mb-1">Chargé</div>
                            <div className="text-xl font-black text-orange-600">12€</div>
                            <div className="text-xs text-gray-500 mt-1">Design détaillé</div>
                          </div>
                          <div className="text-center p-4 bg-white rounded-xl shadow-sm border-2 border-orange-100 hover:shadow-md transition-all duration-200">
                            <div className="text-sm font-bold text-gray-700 mb-1">Mariée</div>
                            <div className="text-xl font-black text-orange-600">20€</div>
                            <div className="text-xs text-gray-500 mt-1">Design premium</div>
                          </div>
                        </div>
                        <div className="mt-4 p-3 bg-white/60 rounded-lg border border-orange-200">
                          <p className="text-sm text-gray-700 text-center font-medium">
                            <span className="text-orange-600">💡</span> 
                            Chaque service inclut une consultation personnalisée et une durée de 1 heure
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    {/* Créneaux disponibles - Design amélioré */}
                    <div className="space-y-4">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-gray-800 flex items-center">
                          <Calendar className="w-6 h-6 mr-3 text-orange-500" />
                          Créneaux disponibles
                        </h3>
                        <div className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
                          {availableSlots.length} créneau{availableSlots.length > 1 ? 's' : ''} disponible{availableSlots.length > 1 ? 's' : ''}
                        </div>
                      </div>
                      
                      {availableSlots.map((slot, index) => {
                        const slotDate = new Date(slot.date);
                        const isToday = slotDate.toDateString() === new Date().toDateString();
                        const isTomorrow = slotDate.toDateString() === new Date(Date.now() + 86400000).toDateString();
                        
                        let dateLabel = formatDate(slot.date);
                        if (isToday) {
                          dateLabel = "Aujourd'hui";
                        } else if (isTomorrow) {
                          dateLabel = "Demain";
                        }
                        
                        return (
                          <div 
                            key={slot.id} 
                            className="bg-white border-2 border-gray-200 rounded-xl p-4 sm:p-5 hover:border-orange-300 hover:shadow-lg transition-all duration-300 group"
                          >
                            {/* Mobile layout - Stack vertically */}
                            <div className="flex flex-col sm:hidden space-y-4">
                              <div className="flex items-center space-x-3">
                                <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                                  <Calendar className="w-6 h-6 text-white" />
                                </div>
                                <div className="flex-1">
                                  <div className="font-bold text-gray-900 flex items-center text-base">
                                    {dateLabel}
                                    {isToday && <span className="ml-2 text-xs bg-red-500 text-white px-2 py-1 rounded-full font-bold animate-pulse">URGENT</span>}
                                    {isTomorrow && <span className="ml-2 text-xs bg-orange-500 text-white px-2 py-1 rounded-full font-bold">BIENTÔT</span>}
                                  </div>
                                  <div className="text-sm text-gray-600 flex items-center mt-1 font-medium">
                                    <Clock className="w-4 h-4 mr-2 text-orange-500" />
                                    <span className="text-gray-800 font-semibold">
                                      {slot.start_time ? `${formatTime(slot.start_time)}` : 'Heure non spécifiée'}
                                    </span>
                                  </div>
                                </div>
                              </div>
                              {/* Mobile Reserve Button - Full width */}
                              <Button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  goToBookingDetails(slot.id);
                                }}
                                className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold py-3 px-4 shadow-lg hover:shadow-xl transition-all duration-300 text-base"
                              >
                                <span className="mr-2">✨</span>
                                Réserver ce créneau
                              </Button>
                            </div>

                            {/* Desktop layout - Side by side */}
                            <div className="hidden sm:flex items-center justify-between">
                              <div className="flex items-center space-x-4 cursor-pointer" onClick={() => goToBookingDetails(slot.id)}>
                                <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                                  <Calendar className="w-7 h-7 text-white" />
                                </div>
                                <div>
                                  <div className="font-bold text-gray-900 flex items-center text-lg">
                                    {dateLabel}
                                    {isToday && <span className="ml-3 text-xs bg-red-500 text-white px-2 py-1 rounded-full font-bold animate-pulse">URGENT</span>}
                                    {isTomorrow && <span className="ml-3 text-xs bg-orange-500 text-white px-2 py-1 rounded-full font-bold">BIENTÔT</span>}
                                  </div>
                                  <div className="text-sm text-gray-600 flex items-center mt-2 font-medium">
                                    <Clock className="w-4 h-4 mr-2 text-orange-500" />
                                    <span className="text-gray-800 font-semibold">
                                      {slot.start_time ? `${formatTime(slot.start_time)}` : 'Heure non spécifiée'}
                                    </span>
                                  </div>
                                </div>
                              </div>
                              
                              <div className="flex items-center space-x-4">
                                <div className="text-right hidden lg:block">
                                  <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Durée</div>
                                  <div className="text-sm font-bold text-gray-800">1 heure</div>
                                </div>
                                <Button 
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    goToBookingDetails(slot.id);
                                  }}
                                  size="lg"
                                  className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold px-6 py-2 shadow-lg group-hover:shadow-xl transition-all duration-300 flex-shrink-0"
                                >
                                  <span className="mr-2">✨</span>
                                  Réserver
                                </Button>
                              </div>
                            </div>
                          </div>
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