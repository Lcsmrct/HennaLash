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
      <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
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
      pending: { label: 'En attente', variant: 'secondary' },
      confirmed: { label: 'Confirmé', variant: 'default' },
      cancelled: { label: 'Annulé', variant: 'destructive' },
      completed: { label: 'Terminé', variant: 'success' }
    };
    
    const statusInfo = statusMap[status] || { label: status, variant: 'secondary' };
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>;
  };

  const getReviewStatusBadge = (status) => {
    const statusMap = {
      pending: { label: 'En attente', variant: 'secondary' },
      approved: { label: 'Approuvé', variant: 'success' },
      rejected: { label: 'Rejeté', variant: 'destructive' }
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
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-orange-200 border-t-orange-600 mb-4"></div>
          <p className="text-lg font-semibold text-gray-700">Chargement de l'administration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50 pt-16">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-orange-600 via-amber-600 to-rose-600 bg-clip-text text-transparent">
              🛠️ Administration
            </h1>
            <p className="text-gray-600 text-lg font-medium mt-2">Gérez les créneaux, rendez-vous et avis</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <MaintenanceModal isAdmin={true} />
            <Button 
              onClick={logout} 
              variant="outline" 
              className="w-full sm:w-auto bg-white/80 backdrop-blur-sm hover:bg-orange-50 border-orange-200 hover:border-orange-300 transition-all duration-300 hover:shadow-lg"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Déconnexion
            </Button>
          </div>
        </div>

        <Tabs defaultValue="appointments" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4 gap-1 h-auto p-1 bg-white/80 backdrop-blur-sm border-2 border-orange-100 shadow-lg rounded-xl">
            <TabsTrigger 
              value="appointments" 
              className="text-xs sm:text-sm py-3 px-1 sm:px-3 min-h-[50px] flex items-center justify-center rounded-lg font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              📅 Rendez-vous
            </TabsTrigger>
            <TabsTrigger 
              value="slots" 
              className="text-xs sm:text-sm py-3 px-1 sm:px-3 min-h-[50px] flex items-center justify-center rounded-lg font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              ⏰ Créneaux
            </TabsTrigger>
            <TabsTrigger 
              value="reviews" 
              className="text-xs sm:text-sm py-3 px-1 sm:px-3 min-h-[50px] flex items-center justify-center rounded-lg font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              ⭐ Avis
            </TabsTrigger>
            <TabsTrigger 
              value="stats" 
              className="text-xs sm:text-sm py-3 px-1 sm:px-3 min-h-[50px] flex items-center justify-center rounded-lg font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              📊 Stats
            </TabsTrigger>
          </TabsList>

          <TabsContent value="appointments" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="mr-2 h-5 w-5" />
                  Gestion des Rendez-vous
                </CardTitle>
                <CardDescription>
                  Gérez tous les rendez-vous clients
                </CardDescription>
              </CardHeader>
              <CardContent>
                {appointments.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">
                    Aucun rendez-vous pour le moment
                  </p>
                ) : (
                  <div className="space-y-4">
                    {appointments.map((appointment) => (
                      <div key={appointment.id} className="border rounded-lg p-4">
                        <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                          <div className="space-y-2 flex-1">
                            <h3 className="font-semibold">
                              {appointment.service_name || 'Service non spécifié'}
                            </h3>
                            <p className="text-sm text-gray-600">
                              <User className="mr-1 h-4 w-4 inline" />
                              {appointment.user_name} ({appointment.user_email})
                            </p>
                            <div className="flex items-center text-sm text-gray-600">
                              <Calendar className="mr-1 h-4 w-4" />
                              {appointment.slot_info && appointment.slot_info.date ? formatDate(appointment.slot_info.date) : 'Date non spécifiée'}
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <Clock className="mr-1 h-4 w-4" />
                              {appointment.slot_info && appointment.slot_info.start_time ? 
                                `${formatTime(appointment.slot_info.start_time)}` 
                                : 'Heure non spécifiée'}
                            </div>
                            {appointment.notes && (
                              <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                                <h4 className="font-medium text-blue-900 mb-2 flex items-center">
                                  <MessageSquare className="mr-1 h-4 w-4" />
                                  Informations Client
                                </h4>
                                <div className="text-sm text-blue-800 whitespace-pre-line">
                                  {appointment.notes}
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="text-right space-y-2 w-full sm:w-auto">
                            {getStatusBadge(appointment.status)}
                            <div className="flex flex-row sm:flex-col gap-2 justify-end">
                              {appointment.status === 'pending' && (
                                <Button 
                                  size="sm" 
                                  onClick={() => updateAppointmentStatus(appointment.id, 'confirmed')}
                                  className="flex-1 sm:flex-none"
                                >
                                  <Check className="h-4 w-4" />
                                  <span className="ml-1 sm:hidden">Confirmer</span>
                                </Button>
                              )}
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => deleteAppointment(appointment.id)}
                                className="flex-1 sm:flex-none"
                              >
                                <Trash2 className="h-4 w-4" />
                                <span className="ml-1 sm:hidden">Supprimer</span>
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="slots" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Clock className="mr-2 h-5 w-5" />
                    Gestion des Créneaux
                  </div>
                  <Dialog open={showSlotDialog} onOpenChange={setShowSlotDialog}>
                    <DialogTrigger asChild>
                      <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        Ajouter un créneau
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Créer un nouveau créneau</DialogTitle>
                        <DialogDescription>
                          Ajoutez un nouveau créneau disponible pour les clients
                        </DialogDescription>
                      </DialogHeader>
                      <form onSubmit={createSlot} className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="date">Date</Label>
                          <Input
                            id="date"
                            type="date"
                            value={slotForm.date}
                            onChange={(e) => setSlotForm({...slotForm, date: e.target.value})}
                            required
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="time">Heure</Label>
                            <Input
                              id="time"
                              type="time"
                              value={slotForm.time}
                              onChange={(e) => setSlotForm({...slotForm, time: e.target.value})}
                              required
                            />
                          </div>
                        </div>
                        <DialogFooter>
                          <Button type="submit" className="bg-blue-600 hover:bg-blue-700">Créer le créneau</Button>
                        </DialogFooter>
                      </form>
                    </DialogContent>
                  </Dialog>
                </CardTitle>
                <CardDescription>
                  Créez et gérez les créneaux disponibles
                </CardDescription>
              </CardHeader>
              <CardContent>
                {slots.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">
                    Aucun créneau créé pour le moment
                  </p>
                ) : (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {slots.map((slot) => (
                      <Card key={slot.id}>
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-2">
                            <h3 className="font-semibold">{slot.service_name}</h3>
                            <Badge variant={slot.is_available ? 'success' : 'secondary'}>
                              {slot.is_available ? 'Disponible' : 'Réservé'}
                            </Badge>
                          </div>
                          <div className="space-y-2 text-sm text-gray-600">
                            <div className="flex items-center">
                              <Calendar className="mr-1 h-4 w-4" />
                              {slot.date ? formatDate(slot.date) : 'Date non spécifiée'}
                            </div>
                            <div className="flex items-center">
                              <Clock className="mr-1 h-4 w-4" />
                              {slot.start_time ? formatTime(slot.start_time) : 'Heure non spécifiée'}
                            </div>

                          </div>
                          <Button 
                            variant="destructive" 
                            size="sm" 
                            className="w-full mt-4"
                            onClick={() => deleteSlot(slot.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Supprimer
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reviews" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Star className="mr-2 h-5 w-5" />
                  Gestion des Avis
                </CardTitle>
                <CardDescription>
                  Approuvez ou rejetez les avis clients
                </CardDescription>
              </CardHeader>
              <CardContent>
                {reviews.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">
                    Aucun avis pour le moment
                  </p>
                ) : (
                  <div className="space-y-4">
                    {reviews.map((review) => (
                      <div key={review.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div className="space-y-2">
                            <div className="flex items-center">
                              <User className="mr-2 h-4 w-4" />
                              <span className="font-semibold">{review.user_name}</span>
                              <div className="ml-4 flex">
                                {[...Array(5)].map((_, i) => (
                                  <Star
                                    key={i}
                                    className={`h-4 w-4 ${
                                      i < review.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                                    }`}
                                  />
                                ))}
                              </div>
                            </div>
                            <p className="text-gray-600">{review.comment}</p>
                            <p className="text-sm text-gray-500">
                              {new Date(review.created_at).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                          <div className="text-right space-y-2">
                            {getReviewStatusBadge(review.status)}
                            {review.status === 'pending' && (
                              <div className="flex gap-2">
                                <Button 
                                  size="sm" 
                                  onClick={() => updateReviewStatus(review.id, 'approved')}
                                >
                                  <Check className="h-4 w-4" />
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="destructive"
                                  onClick={() => updateReviewStatus(review.id, 'rejected')}
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="stats">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Rendez-vous</CardTitle>
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{appointments.length}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Créneaux Créés</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{slots.length}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avis Reçus</CardTitle>
                  <Star className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reviews.length}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">En Attente</CardTitle>
                  <User className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {appointments.filter(a => a.status === 'pending').length}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;