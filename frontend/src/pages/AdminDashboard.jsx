import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import { useCache } from '../hooks/useCache';
import apiService from '../services/apiService';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Calendar, Clock, Star, User, LogOut, Plus, Check, X, Trash2, MessageSquare, Settings, BarChart3, Users, Timer, Award } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from '../hooks/use-toast';
import Navigation from '../components/Navigation';
import MaintenanceModal from '../components/MaintenanceModal';

const AdminDashboard = () => {
  const { user, logout, isAuthenticated } = useAuth();
  
  // ALL hooks must be called before any conditional returns
  const [appointments, setAppointments] = useState([]);
  const [slots, setSlots] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSlotDialog, setShowSlotDialog] = useState(false);
  const [slotForm, setSlotForm] = useState({
    date: '',
    time: '' // Une seule heure (durée fixe 1h)
  });

  useEffect(() => {
    let isMounted = true;
    
    const loadData = async () => {
      // Skip data loading if not authenticated or not admin
      if (!isAuthenticated || !user || user.role !== 'admin') {
        return;
      }
      
      try {
        setLoading(true);
        
        // Appels API individuels avec gestion d'erreur robuste
        const [appointmentsRes, slotsRes, reviewsRes] = await Promise.allSettled([
          apiService.getAppointments(),
          apiService.getSlots(),
          apiService.getAllReviews()
        ]);
        
        // Vérifier si le composant est toujours monté avant setState
        if (!isMounted) return;
        
        // Gestion des résultats avec fallback
        if (appointmentsRes.status === 'fulfilled') {
          setAppointments(appointmentsRes.value || []);
        } else {
          console.error('Error fetching appointments:', appointmentsRes.reason);
          setAppointments([]);
        }
        
        if (slotsRes.status === 'fulfilled') {
          setSlots(slotsRes.value || []);
        } else {
          console.error('Error fetching slots:', slotsRes.reason);
          setSlots([]);
        }
        
        if (reviewsRes.status === 'fulfilled') {
          setReviews(reviewsRes.value || []);
        } else {
          console.error('Error fetching reviews:', reviewsRes.reason);
          setReviews([]);
        }
        
      } catch (error) {
        console.error('Error in loadData:', error);
        if (isMounted) {
          // Initialiser avec des valeurs vides pour éviter les erreurs
          setAppointments([]);
          setSlots([]);
          setReviews([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    loadData();
    
    // Cleanup function
    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, user]);

  // Redirect logic AFTER all hooks are declared
  if (!isAuthenticated) {
    return <Navigate to="/connexion" replace />;
  }

  // Wait for user data to be loaded before checking role
  if (!user) {
    return (
      <div className="min-h-screen bg-slate-50/50">
        <Navigation />
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Chargement...</p>
          </div>
        </div>
      </div>
    );
  }

  if (user.role !== 'admin') {
    return <Navigate to="/mon-espace" replace />;
  }

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Appels API individuels avec gestion d'erreur robuste
      const [appointmentsRes, slotsRes, reviewsRes] = await Promise.allSettled([
        apiService.getAppointments(),
        apiService.getSlots(),
        apiService.getAllReviews()
      ]);
      
      // Gestion des résultats avec fallback
      if (appointmentsRes.status === 'fulfilled') {
        setAppointments(appointmentsRes.value || []);
      } else {
        console.error('Error fetching appointments:', appointmentsRes.reason);
        setAppointments([]);
      }
      
      if (slotsRes.status === 'fulfilled') {
        setSlots(slotsRes.value || []);
      } else {
        console.error('Error fetching slots:', slotsRes.reason);
        setSlots([]);
      }
      
      if (reviewsRes.status === 'fulfilled') {
        setReviews(reviewsRes.value || []);
      } else {
        console.error('Error fetching reviews:', reviewsRes.reason);
        setReviews([]);
      }
      
    } catch (error) {
      console.error('Error in fetchData:', error);
      // Initialiser avec des valeurs vides pour éviter les erreurs
      setAppointments([]);
      setSlots([]);
      setReviews([]);
    } finally {
      setLoading(false);
    }
  };

  const createSlot = async (e) => {
    e.preventDefault();
    try {
      await apiService.createSlot(slotForm);
      
      toast({
        title: "Succès",
        description: "Créneau créé avec succès !"
      });
      
      setShowSlotDialog(false);
      setSlotForm({
        date: '',
        time: ''
      });
      
      fetchData();
    } catch (error) {
      console.error('Error creating slot:', error);
      toast({
        title: "Erreur",
        description: "Impossible de créer le créneau",
        variant: "destructive"
      });
    }
  };

  const updateAppointmentStatus = async (appointmentId, status) => {
    try {
      await apiService.updateAppointmentStatus(appointmentId, status);
      
      toast({
        title: "Succès",
        description: "Rendez-vous mis à jour !"
      });
      
      fetchData();
    } catch (error) {
      console.error('Error updating appointment:', error);
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour le rendez-vous",
        variant: "destructive"
      });
    }
  };

  const deleteAppointment = async (appointmentId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce rendez-vous ?')) return;
    
    try {
      await apiService.deleteAppointment(appointmentId);
      
      toast({
        title: "Succès",
        description: "Rendez-vous supprimé !"
      });
      
      fetchData();
    } catch (error) {
      console.error('Error deleting appointment:', error);
      toast({
        title: "Erreur",
        description: "Impossible de supprimer le rendez-vous",
        variant: "destructive"
      });
    }
  };

  const updateReviewStatus = async (reviewId, status) => {
    try {
      await apiService.updateReviewStatus(reviewId, status);
      
      toast({
        title: "Succès",
        description: `Avis ${status === 'approved' ? 'approuvé' : 'rejeté'} !`
      });
      
      fetchData();
    } catch (error) {
      console.error('Error updating review:', error);
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour l'avis",
        variant: "destructive"
      });
    }
  };

  const deleteSlot = async (slotId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce créneau ?')) return;
    
    try {
      await apiService.deleteSlot(slotId);
      
      toast({
        title: "Succès",
        description: "Créneau supprimé !"
      });
      
      fetchData();
    } catch (error) {
      console.error('Error deleting slot:', error);
      toast({
        title: "Erreur",
        description: "Impossible de supprimer le créneau",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'pending': { label: 'En attente', variant: 'default' },
      'confirmed': { label: 'Confirmé', variant: 'success' },
      'cancelled': { label: 'Annulé', variant: 'destructive' },
      'completed': { label: 'Terminé', variant: 'secondary' }
    };
    const statusInfo = statusMap[status] || { label: status, variant: 'secondary' };
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>;
  };

  // Fonctions pour parser les informations depuis les notes (identiques à ClientDashboard)
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

  const parseInstagramFromNotes = (notes) => {
    if (!notes) return null;
    
    const instagramMatch = notes.match(/📱 Instagram: (.+?)(?:\n|$)/);
    if (instagramMatch) {
      return instagramMatch[1].trim();
    }
    return null;
  };

  const parsePersonnesFromNotes = (notes) => {
    if (!notes) return null;
    
    const personnesMatch = notes.match(/👥 Nombre de personnes: (.+?)(?:\n|$)/);
    if (personnesMatch) {
      return personnesMatch[1].trim();
    }
    return null;
  };

  const parseInfosSuppFromNotes = (notes) => {
    if (!notes) return null;
    
    const infosMatch = notes.match(/ℹ️ Informations supplémentaires:\n(.+?)(?:\n\n|$)/s);
    if (infosMatch) {
      return infosMatch[1].trim();
    }
    return null;
  };

  const getReviewStatusBadge = (status) => {
    const statusMap = {
      pending: { 
        label: 'En attente', 
        className: 'bg-amber-50 text-amber-700 border-amber-200 font-medium'
      },
      approved: { 
        label: 'Approuvé', 
        className: 'bg-emerald-50 text-emerald-700 border-emerald-200 font-medium'
      },
      rejected: { 
        label: 'Rejeté', 
        className: 'bg-red-50 text-red-700 border-red-200 font-medium'
      }
    };
    
    const statusInfo = statusMap[status] || { 
      label: status, 
      className: 'bg-gray-50 text-gray-700 border-gray-200 font-medium'
    };
    
    return (
      <Badge className={`${statusInfo.className} border rounded-lg px-3 py-1`}>
        {statusInfo.label}
      </Badge>
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
      <div className="min-h-screen bg-slate-50/50 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="relative mx-auto w-20 h-20 mb-6">
            <div className="absolute inset-0 rounded-full border-4 border-orange-100"></div>
            <div className="absolute inset-0 rounded-full border-4 border-orange-500 border-t-transparent animate-spin"></div>
            <div className="absolute inset-2 rounded-full bg-gradient-to-r from-orange-400 to-amber-500 flex items-center justify-center">
              <Settings className="w-6 h-6 text-white animate-pulse" />
            </div>
          </div>
          <p className="text-xl font-semibold text-slate-700 mb-2">Administration</p>
          <p className="text-slate-500">Chargement des données...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50/50">
      <Navigation />
      
      <div className="pt-20 pb-8">
        {/* Modern Header */}
        <div className="bg-white border-b border-slate-200/60 shadow-sm">
          <div className="container mx-auto px-6 py-8">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-amber-500 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-500/25">
                  <Settings className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-slate-900 mb-1">
                    Administration
                  </h1>
                  <p className="text-slate-600 font-medium">
                    Tableau de bord • {appointments.length} rendez-vous • {slots.length} créneaux
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <MaintenanceModal isAdmin={true} />
                <Button 
                  onClick={logout} 
                  variant="outline" 
                  className="bg-white hover:bg-slate-50 border-slate-300 hover:border-slate-400 text-slate-700 font-medium shadow-sm transition-all duration-200"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Déconnexion
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="container mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-2xl p-6 border-2 border-orange-100 hover:border-orange-200 shadow-sm hover:shadow-md transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <Badge variant="secondary" className="bg-blue-50 text-blue-700 border-blue-200">
                  Total
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold text-slate-900">{appointments.length}</p>
                <p className="text-sm text-slate-600 font-medium">Rendez-vous</p>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border-2 border-orange-100 hover:border-orange-200 shadow-sm hover:shadow-md transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-orange-500/10 rounded-xl flex items-center justify-center">
                  <Timer className="w-6 h-6 text-orange-600" />
                </div>
                <Badge variant="secondary" className="bg-orange-50 text-orange-700 border-orange-200">
                  Actifs
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold text-slate-900">{slots.filter(s => s.is_available).length}</p>
                <p className="text-sm text-slate-600 font-medium">Créneaux dispos</p>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border-2 border-orange-100 hover:border-orange-200 shadow-sm hover:shadow-md transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-yellow-500/10 rounded-xl flex items-center justify-center">
                  <Award className="w-6 h-6 text-yellow-600" />
                </div>
                <Badge variant="secondary" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                  Qualité
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold text-slate-900">{reviews.filter(r => r.status === 'approved').length}</p>
                <p className="text-sm text-slate-600 font-medium">Avis validés</p>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border-2 border-orange-100 hover:border-orange-200 shadow-sm hover:shadow-md transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-emerald-600" />
                </div>
                <Badge variant="secondary" className="bg-emerald-50 text-emerald-700 border-emerald-200">
                  En attente
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold text-slate-900">{appointments.filter(a => a.status === 'pending').length}</p>
                <p className="text-sm text-slate-600 font-medium">À confirmer</p>
              </div>
            </div>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="appointments" className="space-y-6">
            <div className="bg-white rounded-2xl p-2 border border-slate-200/60 shadow-sm">
              <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 bg-transparent h-auto p-0 gap-2">
                <TabsTrigger 
                  value="appointments" 
                  className="flex items-center gap-2 p-4 rounded-xl font-semibold text-slate-600 hover:text-slate-900 data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-orange-500/25 transition-all duration-300"
                >
                  <Users className="w-4 h-4" />
                  <span className="hidden sm:inline">Rendez-vous</span>
                </TabsTrigger>
                <TabsTrigger 
                  value="slots" 
                  className="flex items-center gap-2 p-4 rounded-xl font-semibold text-slate-600 hover:text-slate-900 data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-orange-500/25 transition-all duration-300"
                >
                  <Timer className="w-4 h-4" />
                  <span className="hidden sm:inline">Créneaux</span>
                </TabsTrigger>
                <TabsTrigger 
                  value="reviews" 
                  className="flex items-center gap-2 p-4 rounded-xl font-semibold text-slate-600 hover:text-slate-900 data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-orange-500/25 transition-all duration-300"
                >
                  <Award className="w-4 h-4" />
                  <span className="hidden sm:inline">Avis</span>
                </TabsTrigger>
                <TabsTrigger 
                  value="stats" 
                  className="flex items-center gap-2 p-4 rounded-xl font-semibold text-slate-600 hover:text-slate-900 data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-orange-500/25 transition-all duration-300"
                >
                  <BarChart3 className="w-4 h-4" />
                  <span className="hidden sm:inline">Statistiques</span>
                </TabsTrigger>
              </TabsList>
            </div>

            {/* Appointments Tab */}
            <TabsContent value="appointments" className="space-y-6">
              <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm">
                <div className="p-6 border-b border-slate-200/60">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 bg-blue-500/10 rounded-xl flex items-center justify-center">
                      <Users className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-slate-900">Gestion des Rendez-vous</h2>
                      <p className="text-slate-600">Gérez et suivez tous les rendez-vous clients</p>
                    </div>
                  </div>
                </div>
                
                <div className="p-6">
                  {appointments.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Calendar className="w-8 h-8 text-slate-400" />
                      </div>
                      <p className="text-slate-500 font-medium">Aucun rendez-vous pour le moment</p>
                      <p className="text-slate-400 text-sm mt-1">Les nouveaux rendez-vous apparaîtront ici</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {appointments.map((appointment) => (
                        <div key={appointment.id} className="bg-slate-50/50 rounded-2xl p-6 border-2 border-orange-200 hover:border-orange-300 hover:shadow-md transition-all duration-200">
                          <div className="flex flex-col lg:flex-row justify-between items-start gap-6">
                            <div className="flex-1 space-y-4">
                              <div className="flex items-start justify-between">
                                <div>
                                  <h3 className="text-lg font-bold text-slate-900 mb-1">
                                    {appointment.service_name || 'Service non spécifié'}
                                  </h3>
                                  <div className="flex items-center gap-2 text-slate-600">
                                    <User className="w-4 h-4" />
                                    <span className="font-medium">{appointment.user_name}</span>
                                    <span className="text-slate-400">•</span>
                                    <span className="text-sm">{appointment.user_email}</span>
                                  </div>
                                </div>
                                {getStatusBadge(appointment.status)}
                              </div>
                              
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="flex items-center gap-3 p-3 bg-white rounded-xl border-2 border-orange-100 hover:border-orange-200 transition-colors">
                                  <div className="w-8 h-8 bg-blue-500/10 rounded-lg flex items-center justify-center">
                                    <Calendar className="w-4 h-4 text-blue-600" />
                                  </div>
                                  <div>
                                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Date</p>
                                    <p className="text-sm font-semibold text-slate-900">
                                      {appointment.slot_info && appointment.slot_info.date ? 
                                        formatDate(appointment.slot_info.date) : 
                                        'Date non spécifiée'
                                      }
                                    </p>
                                  </div>
                                </div>
                                
                                <div className="flex items-center gap-3 p-3 bg-white rounded-xl border-2 border-orange-100 hover:border-orange-200 transition-colors">
                                  <div className="w-8 h-8 bg-orange-500/10 rounded-lg flex items-center justify-center">
                                    <Clock className="w-4 h-4 text-orange-600" />
                                  </div>
                                  <div>
                                    <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Heure</p>
                                    <p className="text-sm font-semibold text-slate-900">
                                      {appointment.slot_info && appointment.slot_info.start_time ? 
                                        formatTime(appointment.slot_info.start_time) : 
                                        'Heure non spécifiée'
                                      }
                                    </p>
                                  </div>
                                </div>
                              </div>

                              {appointment.notes && (
                                <div className="bg-blue-50/50 rounded-xl p-4 border border-blue-200/50">
                                  <div className="flex items-start gap-3">
                                    <div className="w-8 h-8 bg-blue-500/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                                      <MessageSquare className="w-4 h-4 text-blue-600" />
                                    </div>
                                    <div className="flex-1">
                                      <p className="text-xs text-blue-600 font-medium uppercase tracking-wide mb-2">Informations Client</p>
                                      <div className="text-sm text-blue-900 whitespace-pre-line leading-relaxed">
                                        {appointment.notes}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            <div className="flex flex-row lg:flex-col gap-2 w-full lg:w-auto">
                              {appointment.status === 'pending' && (
                                <Button 
                                  size="sm" 
                                  onClick={() => updateAppointmentStatus(appointment.id, 'confirmed')}
                                  className="flex-1 lg:flex-none bg-emerald-600 hover:bg-emerald-700 text-white font-medium shadow-sm"
                                >
                                  <Check className="w-4 h-4 mr-2" />
                                  Confirmer
                                </Button>
                              )}
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => deleteAppointment(appointment.id)}
                                className="flex-1 lg:flex-none border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 font-medium"
                              >
                                <Trash2 className="w-4 h-4 mr-2" />
                                Supprimer
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>

            {/* Slots Tab */}
            <TabsContent value="slots" className="space-y-6">
              <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm">
                <div className="p-6 border-b border-slate-200/60">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-orange-500/10 rounded-xl flex items-center justify-center">
                        <Timer className="w-5 h-5 text-orange-600" />
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-slate-900">Gestion des Créneaux</h2>
                        <p className="text-slate-600">Créez et gérez les créneaux disponibles</p>
                      </div>
                    </div>
                    
                    <Dialog open={showSlotDialog} onOpenChange={setShowSlotDialog}>
                      <DialogTrigger asChild>
                        <Button className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-medium shadow-lg shadow-orange-500/25">
                          <Plus className="mr-2 h-4 w-4" />
                          Nouveau créneau
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="sm:max-w-md">
                        <DialogHeader>
                          <DialogTitle className="text-xl font-bold">Créer un nouveau créneau</DialogTitle>
                          <DialogDescription className="text-slate-600">
                            Ajoutez un nouveau créneau disponible pour les clients
                          </DialogDescription>
                        </DialogHeader>
                        <form onSubmit={createSlot} className="space-y-6">
                          <div className="space-y-4">
                            <div>
                              <Label htmlFor="date" className="text-sm font-semibold text-slate-700">Date</Label>
                              <Input
                                id="date"
                                type="date"
                                value={slotForm.date}
                                onChange={(e) => setSlotForm({...slotForm, date: e.target.value})}
                                className="mt-1.5 border-slate-300 focus:border-orange-500 focus:ring-orange-500"
                                required
                              />
                            </div>
                            <div>
                              <Label htmlFor="time" className="text-sm font-semibold text-slate-700">Heure de début</Label>
                              <Input
                                id="time"
                                type="time"
                                value={slotForm.time}
                                onChange={(e) => setSlotForm({...slotForm, time: e.target.value})}
                                className="mt-1.5 border-slate-300 focus:border-orange-500 focus:ring-orange-500"
                                required
                              />
                              <p className="text-xs text-slate-500 mt-1.5">Durée automatique : 1 heure</p>
                            </div>
                          </div>
                          <DialogFooter>
                            <Button 
                              type="button" 
                              variant="outline" 
                              onClick={() => setShowSlotDialog(false)}
                              className="border-slate-300 text-slate-700"
                            >
                              Annuler
                            </Button>
                            <Button 
                              type="submit" 
                              className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-medium"
                            >
                              Créer le créneau
                            </Button>
                          </DialogFooter>
                        </form>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
                
                <div className="p-6">
                  {slots.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Timer className="w-8 h-8 text-slate-400" />
                      </div>
                      <p className="text-slate-500 font-medium">Aucun créneau créé pour le moment</p>
                      <p className="text-slate-400 text-sm mt-1">Créez votre premier créneau avec le bouton ci-dessus</p>
                    </div>
                  ) : (
                    <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
                      {slots.map((slot) => (
                        <div key={slot.id} className="bg-slate-50/50 rounded-2xl p-5 border-2 border-orange-200 hover:border-orange-300 hover:shadow-md transition-all duration-200">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <h3 className="font-semibold text-slate-900 mb-1">Créneau disponible</h3>
                              <Badge className={slot.is_available ? 
                                'bg-emerald-50 text-emerald-700 border-emerald-200' : 
                                'bg-red-50 text-red-700 border-red-200'
                              }>
                                {slot.is_available ? 'Disponible' : 'Réservé'}
                              </Badge>
                            </div>
                          </div>
                          
                          <div className="space-y-3 mb-4">
                            <div className="flex items-center gap-3 p-3 bg-white rounded-xl border-2 border-orange-100 hover:border-orange-200 transition-colors">
                              <div className="w-8 h-8 bg-blue-500/10 rounded-lg flex items-center justify-center">
                                <Calendar className="w-4 h-4 text-blue-600" />
                              </div>
                              <div>
                                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Date</p>
                                <p className="text-sm font-semibold text-slate-900">
                                  {slot.date ? formatDate(slot.date) : 'Date non spécifiée'}
                                </p>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-3 p-3 bg-white rounded-xl border-2 border-orange-100 hover:border-orange-200 transition-colors">
                              <div className="w-8 h-8 bg-orange-500/10 rounded-lg flex items-center justify-center">
                                <Clock className="w-4 h-4 text-orange-600" />
                              </div>
                              <div>
                                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Heure</p>
                                <p className="text-sm font-semibold text-slate-900">
                                  {slot.start_time ? formatTime(slot.start_time) : 'Heure non spécifiée'}
                                </p>
                              </div>
                            </div>
                          </div>
                          
                          <Button 
                            variant="outline"
                            size="sm" 
                            className="w-full border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 font-medium"
                            onClick={() => deleteSlot(slot.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Supprimer le créneau
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>

            {/* Reviews Tab */}
            <TabsContent value="reviews" className="space-y-6">
              <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm">
                <div className="p-6 border-b border-slate-200/60">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 bg-yellow-500/10 rounded-xl flex items-center justify-center">
                      <Award className="w-5 h-5 text-yellow-600" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-slate-900">Gestion des Avis</h2>
                      <p className="text-slate-600">Approuvez ou rejetez les avis clients</p>
                    </div>
                  </div>
                </div>
                
                <div className="p-6">
                  {reviews.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Star className="w-8 h-8 text-slate-400" />
                      </div>
                      <p className="text-slate-500 font-medium">Aucun avis pour le moment</p>
                      <p className="text-slate-400 text-sm mt-1">Les avis clients apparaîtront ici</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {reviews.map((review) => (
                        <div key={review.id} className="bg-slate-50/50 rounded-2xl p-6 border-2 border-orange-200 hover:border-orange-300 hover:shadow-md transition-all duration-200">
                          <div className="flex flex-col lg:flex-row justify-between items-start gap-6">
                            <div className="flex-1 space-y-4">
                              <div className="flex items-start justify-between">
                                <div className="flex items-center gap-3">
                                  <div className="w-10 h-10 bg-blue-500/10 rounded-xl flex items-center justify-center">
                                    <User className="w-5 h-5 text-blue-600" />
                                  </div>
                                  <div>
                                    <p className="font-semibold text-slate-900">{review.user_name}</p>
                                    <div className="flex items-center gap-1 mt-1">
                                      {[...Array(5)].map((_, i) => (
                                        <Star
                                          key={i}
                                          className={`h-4 w-4 ${
                                            i < review.rating ? 'text-yellow-400 fill-current' : 'text-slate-300'
                                          }`}
                                        />
                                      ))}
                                      <span className="text-sm text-slate-600 ml-2">{review.rating}/5</span>
                                    </div>
                                  </div>
                                </div>
                                {getReviewStatusBadge(review.status)}
                              </div>
                              
                              <div className="bg-white rounded-xl p-4 border-2 border-orange-100 hover:border-orange-200 transition-colors">
                                <p className="text-slate-700 leading-relaxed">{review.comment}</p>
                              </div>
                              
                              <p className="text-sm text-slate-500">
                                Publié le {new Date(review.created_at).toLocaleDateString('fr-FR', {
                                  day: 'numeric',
                                  month: 'long',
                                  year: 'numeric'
                                })}
                              </p>
                            </div>
                            
                            {review.status === 'pending' && (
                              <div className="flex flex-row lg:flex-col gap-2 w-full lg:w-auto">
                                <Button 
                                  size="sm" 
                                  onClick={() => updateReviewStatus(review.id, 'approved')}
                                  className="flex-1 lg:flex-none bg-emerald-600 hover:bg-emerald-700 text-white font-medium"
                                >
                                  <Check className="w-4 h-4 mr-2" />
                                  Approuver
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => updateReviewStatus(review.id, 'rejected')}
                                  className="flex-1 lg:flex-none border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 font-medium"
                                >
                                  <X className="w-4 h-4 mr-2" />
                                  Rejeter
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>

            {/* Stats Tab */}
            <TabsContent value="stats" className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <div className="bg-white rounded-2xl p-6 border-2 border-orange-100 hover:border-orange-200 shadow-sm hover:shadow-md transition-all duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center">
                      <Users className="w-6 h-6 text-blue-600" />
                    </div>
                    <Badge variant="secondary" className="bg-blue-50 text-blue-700 border-blue-200">
                      Total
                    </Badge>
                  </div>
                  <div className="space-y-1">
                    <p className="text-2xl font-bold text-slate-900">{appointments.length}</p>
                    <p className="text-sm text-slate-600 font-medium">Total Rendez-vous</p>
                  </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border-2 border-orange-100 hover:border-orange-200 shadow-sm hover:shadow-md transition-all duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-orange-500/10 rounded-xl flex items-center justify-center">
                      <Timer className="w-6 h-6 text-orange-600" />
                    </div>
                    <Badge variant="secondary" className="bg-orange-50 text-orange-700 border-orange-200">
                      Gestion
                    </Badge>
                  </div>
                  <div className="space-y-1">
                    <p className="text-2xl font-bold text-slate-900">{slots.length}</p>
                    <p className="text-sm text-slate-600 font-medium">Créneaux Créés</p>
                  </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border-2 border-orange-100 hover:border-orange-200 shadow-sm hover:shadow-md transition-all duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-yellow-500/10 rounded-xl flex items-center justify-center">
                      <Award className="w-6 h-6 text-yellow-600" />
                    </div>
                    <Badge variant="secondary" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                      Qualité
                    </Badge>
                  </div>
                  <div className="space-y-1">
                    <p className="text-2xl font-bold text-slate-900">{reviews.length}</p>
                    <p className="text-sm text-slate-600 font-medium">Avis Reçus</p>
                  </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border-2 border-orange-100 hover:border-orange-200 shadow-sm hover:shadow-md transition-all duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center">
                      <BarChart3 className="w-6 h-6 text-emerald-600" />
                    </div>
                    <Badge variant="secondary" className="bg-emerald-50 text-emerald-700 border-emerald-200">
                      Attente
                    </Badge>
                  </div>
                  <div className="space-y-1">
                    <p className="text-2xl font-bold text-slate-900">
                      {appointments.filter(a => a.status === 'pending').length}
                    </p>
                    <p className="text-sm text-slate-600 font-medium">En Attente</p>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;