import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import { useCache } from '../hooks/useCache';
import apiService from '../services/apiService';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Calendar, Clock, Star, User, LogOut, Plus, Check, X, Trash2, MessageSquare } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from '../hooks/use-toast';
import Navigation from '../components/Navigation';

const AdminDashboard = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [slots, setSlots] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSlotDialog, setShowSlotDialog] = useState(false);
  const [slotForm, setSlotForm] = useState({
    date: '',
    time: '' // Une seule heure (durée fixe 1h)
  });

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  // Redirect if not authenticated or not admin
  if (!isAuthenticated) {
    return <Navigate to="/connexion" replace />;
  }

  if (user?.role !== 'admin') {
    return <Navigate to="/mon-espace" replace />;
  }

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [appointmentsRes, slotsRes, reviewsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/appointments`),
        axios.get(`${API_BASE_URL}/api/slots`),
        axios.get(`${API_BASE_URL}/api/reviews?approved_only=false`)
      ]);
      
      setAppointments(appointmentsRes.data);
      setSlots(slotsRes.data);
      setReviews(reviewsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast({
        title: "Erreur",
        description: "Impossible de charger les données",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const createSlot = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/api/slots`, slotForm);
      
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
      await axios.put(`${API_BASE_URL}/api/appointments/${appointmentId}`, {
        status: status
      });
      
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
      await axios.delete(`${API_BASE_URL}/api/appointments/${appointmentId}`);
      
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
      await axios.put(`${API_BASE_URL}/api/reviews/${reviewId}`, {
        status: status
      });
      
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
      await axios.delete(`${API_BASE_URL}/api/slots/${slotId}`);
      
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          <p className="mt-4">Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Panneau d'Administration
            </h1>
            <p className="text-gray-600">Gérez les créneaux, rendez-vous et avis</p>
          </div>
          <Button onClick={logout} variant="outline">
            <LogOut className="mr-2 h-4 w-4" />
            Déconnexion
          </Button>
        </div>

        <Tabs defaultValue="appointments" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="appointments">Rendez-vous</TabsTrigger>
            <TabsTrigger value="slots">Créneaux</TabsTrigger>
            <TabsTrigger value="reviews">Avis</TabsTrigger>
            <TabsTrigger value="stats">Statistiques</TabsTrigger>
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
                        <div className="flex justify-between items-start">
                          <div className="space-y-2">
                            <h3 className="font-semibold">
                              {appointment.service_name || 'Service non spécifié'}
                            </h3>
                            <p className="text-sm text-gray-600">
                              <User className="mr-1 h-4 w-4 inline" />
                              {appointment.user_name} ({appointment.user_email})
                            </p>
                            <div className="flex items-center text-sm text-gray-600">
                              <Calendar className="mr-1 h-4 w-4" />
                              {appointment.slot_info ? formatDate(appointment.slot_info.date) : 'Date non spécifiée'}
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <Clock className="mr-1 h-4 w-4" />
                              {appointment.slot_info ? 
                                `${formatTime(appointment.slot_info.start_time)} - ${formatTime(appointment.slot_info.end_time)}` 
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
                          <div className="text-right space-y-2">
                            {getStatusBadge(appointment.status)}
                            <p className="text-lg font-semibold">
                              {appointment.service_price || 0}€
                            </p>
                            <div className="flex gap-2">
                              {appointment.status === 'pending' && (
                                <Button 
                                  size="sm" 
                                  onClick={() => updateAppointmentStatus(appointment.id, 'confirmed')}
                                >
                                  <Check className="h-4 w-4" />
                                </Button>
                              )}
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => deleteAppointment(appointment.id)}
                              >
                                <Trash2 className="h-4 w-4" />
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
                              {formatDate(slot.date)}
                            </div>
                            <div className="flex items-center">
                              <Clock className="mr-1 h-4 w-4" />
                              {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                            </div>
                            <p className="text-lg font-semibold text-primary">
                              {slot.price}€
                            </p>
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
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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