import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Label } from '../components/ui/label';
import { Calendar, Check, X, Clock, MessageSquare, Trash2, Users } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import apiService from '../services/apiService';
import LoadingSpinner from '../components/LoadingSpinner';
import Navigation from '../components/Navigation';

const AdminDashboard = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [slots, setSlots] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSlotDialog, setShowSlotDialog] = useState(false);
  const [newSlot, setNewSlot] = useState({
    date: '',
    time: ''
  });

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      navigate('/connexion');
      return;
    }
    fetchData();
  }, [isAuthenticated, user, navigate]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [appointmentsData, slotsData, reviewsData] = await Promise.all([
        apiService.getAppointments(),
        apiService.getSlots(),
        apiService.getAllReviews()
      ]);
      
      setAppointments(appointmentsData || []);
      setSlots(slotsData || []);
      setReviews(reviewsData || []);
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

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Date non spécifiée';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch (error) {
      return 'Date non spécifiée';
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'Heure non spécifiée';
    return timeString;
  };

  const createSlot = async (e) => {
    e.preventDefault();
    
    if (!newSlot.date || !newSlot.time) {
      toast({
        title: "Erreur",
        description: "Veuillez remplir tous les champs",
        variant: "destructive"
      });
      return;
    }

    try {
      await apiService.createSlot({
        date: newSlot.date,
        time: newSlot.time
      });
      
      toast({
        title: "Succès",
        description: "Créneau créé avec succès",
      });
      
      setNewSlot({ date: '', time: '' });
      setShowSlotDialog(false);
      fetchData();
    } catch (error) {
      console.error('Error creating slot:', error);
      toast({
        title: "Erreur",
        description: error.response?.data?.detail || "Impossible de créer le créneau",
        variant: "destructive"
      });
    }
  };

  const updateAppointmentStatus = async (appointmentId, status) => {
    try {
      await apiService.updateAppointmentStatus(appointmentId, status);
      setAppointments(appointments.map(app => 
        app.id === appointmentId 
          ? { ...app, status }
          : app
      ));
      toast({
        title: "Succès",
        description: `Rendez-vous ${status === 'confirmed' ? 'confirmé' : 'mis à jour'} avec succès`,
      });
    } catch (error) {
      console.error('Error updating appointment:', error);
      toast({
        title: "Erreur",
        description: error.response?.data?.detail || "Impossible de mettre à jour le rendez-vous",
        variant: "destructive"
      });
    }
  };

  const deleteAppointment = async (appointmentId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer définitivement ce rendez-vous ?')) {
      return;
    }
    
    try {
      await apiService.deleteAppointment(appointmentId);
      setAppointments(appointments.filter(app => app.id !== appointmentId));
      toast({
        title: "Succès",
        description: "Rendez-vous supprimé avec succès",
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

  const cancelAppointment = async (appointmentId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir annuler ce rendez-vous ? Le client sera automatiquement notifié par email.')) {
      return;
    }
    
    try {
      await apiService.cancelAppointment(appointmentId);
      // Update the appointment status in the list
      setAppointments(appointments.map(app => 
        app.id === appointmentId 
          ? { ...app, status: 'cancelled' }
          : app
      ));
      toast({
        title: "Succès",
        description: "Rendez-vous annulé avec succès et client notifié par email",
      });
    } catch (error) {
      console.error('Error cancelling appointment:', error);
      toast({
        title: "Erreur",
        description: error.response?.data?.detail || "Impossible d'annuler le rendez-vous",
        variant: "destructive"
      });
    }
  };

  // Fonction pour vérifier si un RDV est passé de plus de 24h
  const isAppointmentOlderThan24Hours = (appointment) => {
    if (!appointment.slot_info || !appointment.slot_info.date || !appointment.slot_info.start_time) {
      return false;
    }
    
    try {
      // Créer la date/heure du RDV
      const appointmentDate = new Date(appointment.slot_info.date);
      const [hours, minutes] = appointment.slot_info.start_time.split(':');
      appointmentDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      
      // Calculer la différence avec maintenant
      const now = new Date();
      const diffInHours = (now - appointmentDate) / (1000 * 60 * 60);
      
      return diffInHours > 24;
    } catch (error) {
      console.error('Error calculating appointment age:', error);
      return false;
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
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce créneau ?')) {
      return;
    }
    
    try {
      await apiService.deleteSlot(slotId);
      setSlots(slots.filter(slot => slot.id !== slotId));
      toast({
        title: "Succès",
        description: "Créneau supprimé avec succès",
      });
    } catch (error) {
      console.error('Error deleting slot:', error);
      toast({
        title: "Erreur",
        description: error.response?.data?.detail || "Impossible de supprimer le créneau",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'pending': { label: 'En attente', variant: 'secondary' },
      'confirmed': { label: 'Confirmé', variant: 'default' },
      'completed': { label: 'Terminé', variant: 'success' },
      'cancelled': { label: 'Annulé', variant: 'destructive' }
    };

    const config = statusConfig[status] || { label: status, variant: 'secondary' };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  // Fonctions pour parser les informations depuis les notes (identiques à ClientDashboard)
  const parseLieuFromNotes = (notes) => {
    if (!notes) return null;
    
    const salonMatch = notes.match(/📍\s*Lieu\s*:\s*salon/i);
    const domicileMatch = notes.match(/📍\s*Lieu\s*:\s*domicile/i);
    const evenementMatch = notes.match(/📍\s*Lieu\s*:\s*evenement/i);
    
    if (salonMatch) return 'Chez moi';
    if (domicileMatch) return 'Chez vous';  
    if (evenementMatch) return 'Autre';
    
    return null;
  };

  const parseInstagramFromNotes = (notes) => {
    if (!notes) return null;
    const match = notes.match(/📱\s*Instagram\s*:\s*([^\n\r]+)/i);
    return match ? match[1].trim() : null;
  };

  const parsePersonnesFromNotes = (notes) => {
    if (!notes) return null;
    const match = notes.match(/👥\s*Nombre de personnes\s*:\s*([^\n\r]+)/i);
    return match ? match[1].trim() : null;
  };

  const parseActualNotesFromNotes = (notes) => {
    if (!notes) return null;
    
    // Chercher d'abord les informations supplémentaires dans le format "ℹ️ Informations supplémentaires:\n{contenu}"
    const infoMatch = notes.match(/ℹ️\s*Informations supplémentaires\s*:\s*\n(.+?)(?=\n\n|$)/s);
    if (infoMatch) {
      return infoMatch[1].trim();
    }
    
    // Si pas trouvé, supprimer toutes les métadonnées structurées et retourner le reste
    let cleanNotes = notes
      .replace(/📍\s*Lieu\s*:\s*[^\n\r]+/gi, '')
      .replace(/👥\s*Nombre de personnes\s*:\s*[^\n\r]+/gi, '')
      .replace(/📱\s*Instagram\s*:\s*[^\n\r]+/gi, '')
      .replace(/ℹ️\s*Informations\s*supplémentaires\s*:\s*[^\n\r]+/gi, '')
      .trim();
    
    // Nettoyer les sauts de ligne multiples
    cleanNotes = cleanNotes.replace(/\n\s*\n/g, '\n').trim();
    
    return cleanNotes || null;
  };

  if (!isAuthenticated || user?.role !== 'admin') {
    return <div>Accès non autorisé</div>;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-100">
        <Navigation />
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-100">
      <Navigation />
      <div className="pt-20 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-4">
            🎨 Espace Administrateur
          </h1>
          <p className="text-gray-600 text-lg">Gérez vos rendez-vous, créneaux et avis clients</p>
          <div className="mt-4">
            <Button 
              onClick={handleLogout} 
              variant="outline"
              className="bg-white/80 backdrop-blur-sm border-orange-200 text-orange-600 hover:bg-orange-50 font-medium"
            >
              Se déconnecter
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="appointments" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8 bg-white/60 backdrop-blur-sm rounded-2xl p-2 shadow-lg">
            <TabsTrigger 
              value="appointments" 
              className="rounded-xl font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              📅 Rendez-vous
            </TabsTrigger>
            <TabsTrigger 
              value="slots" 
              className="rounded-xl font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              🕐 Créneaux
            </TabsTrigger>
            <TabsTrigger 
              value="reviews" 
              className="rounded-xl font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-amber-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
            >
              ⭐ Avis
            </TabsTrigger>
          </TabsList>

          {/* Appointments Tab */}
          <TabsContent value="appointments">
            <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-100 shadow-xl rounded-2xl">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-t-2xl">
                <CardTitle className="flex items-center">
                  <Calendar className="mr-2 h-6 w-6" />
                  Rendez-vous ({appointments.length})
                </CardTitle>
                <CardDescription className="text-orange-100">
                  Gérez les réservations de vos clients
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {appointments.map((appointment) => {
                    const lieu = parseLieuFromNotes(appointment.notes);
                    const instagram = parseInstagramFromNotes(appointment.notes);
                    const personnes = parsePersonnesFromNotes(appointment.notes);
                    const actualNotes = parseActualNotesFromNotes(appointment.notes);
                    const canDelete = isAppointmentOlderThan24Hours(appointment);
                    
                    return (
                      <div key={appointment.id} className="border-2 border-orange-100 rounded-2xl p-6 bg-gradient-to-r from-white/90 to-orange-50/50 shadow-lg hover:shadow-xl transition-all duration-300">
                        <div className="flex flex-col lg:flex-row gap-4">
                          <div className="flex-1">
                            <div className="flex items-start justify-between mb-4">
                              <div>
                                <h3 className="font-bold text-xl text-gray-900 mb-2 flex items-center">
                                  <span className="mr-2">🎨</span>
                                  {appointment.service_name || 'Service non spécifié'}
                                </h3>
                                <div className="flex items-center gap-4 text-sm text-gray-600">
                                  <div className="bg-white/80 rounded-lg px-3 py-2 shadow-sm">
                                    <Calendar className="w-4 h-4 inline mr-2 text-orange-500" />
                                    {appointment.slot_info ? formatDate(appointment.slot_info.date) : 'Date non spécifiée'}
                                  </div>
                                  <div className="bg-white/80 rounded-lg px-3 py-2 shadow-sm">
                                    <Clock className="w-4 h-4 inline mr-2 text-orange-500" />
                                    {appointment.slot_info ? formatTime(appointment.slot_info.start_time) : 'Heure non spécifiée'}
                                  </div>
                                </div>
                              </div>
                              <div className="flex flex-col items-end gap-2">
                                {getStatusBadge(appointment.status)}
                                <div className="bg-gradient-to-r from-orange-500 to-amber-500 text-white px-3 py-1 rounded-xl font-bold">
                                  {appointment.service_price || 0}€
                                </div>
                              </div>
                            </div>
                            
                            {/* Informations utilisateur */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                              <div className="bg-white/60 rounded-xl p-3 border border-orange-200">
                                <div className="flex items-center">
                                  <Users className="w-5 h-5 mr-3 text-orange-500" />
                                  <div>
                                    <div className="text-xs text-gray-500 uppercase font-medium">Client</div>
                                    <div className="font-semibold text-gray-800">
                                      {appointment.user_name || 'Utilisateur inconnu'}
                                    </div>
                                    <div className="text-sm text-gray-600">
                                      {appointment.user_email || 'Email non disponible'}
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {lieu && (
                                <div className="bg-white/60 rounded-xl p-3 border border-orange-200">
                                  <div className="flex items-center">
                                    <div className="w-8 h-8 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mr-3">
                                      <span className="text-sm">📍</span>
                                    </div>
                                    <div>
                                      <div className="text-xs text-gray-500 uppercase font-medium">Lieu</div>
                                      <div className="font-semibold text-gray-800">{lieu}</div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Informations supplémentaires */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                              {personnes && (
                                <div className="bg-white/60 rounded-xl p-3 border border-orange-200">
                                  <div className="flex items-center">
                                    <div className="w-8 h-8 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mr-3">
                                      <span className="text-sm">👥</span>
                                    </div>
                                    <div>
                                      <div className="text-xs text-gray-500 uppercase font-medium">Personnes</div>
                                      <div className="font-semibold text-gray-800">{personnes}</div>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {instagram && (
                                <div className="bg-white/60 rounded-xl p-3 border border-orange-200">
                                  <div className="flex items-center">
                                    <div className="w-8 h-8 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center mr-3">
                                      <span className="text-sm">📱</span>
                                    </div>
                                    <div>
                                      <div className="text-xs text-gray-500 uppercase font-medium">Instagram</div>
                                      <div className="font-semibold text-gray-800">{instagram}</div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Notes utilisateur uniquement */}
                            {actualNotes && (
                              <div className="bg-white/60 rounded-xl p-3 border border-orange-200 mb-4">
                                <div className="flex items-start">
                                  <MessageSquare className="w-5 h-5 mr-3 flex-shrink-0 mt-1 text-orange-500" />
                                  <div>
                                    <div className="text-xs text-gray-500 uppercase font-medium mb-1">Notes du client</div>
                                    <div className="text-sm text-gray-700 whitespace-pre-line">
                                      {actualNotes}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {/* Actions - Boutons admin nettoyés */}
                            <div className="flex flex-col sm:flex-row gap-3 justify-start">
                              {appointment.status === 'pending' && (
                                <Button 
                                  size="sm" 
                                  onClick={() => updateAppointmentStatus(appointment.id, 'confirmed')}
                                  className="w-full sm:w-auto min-w-[120px] bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-medium shadow-md hover:shadow-lg transition-all duration-200"
                                >
                                  <Check className="w-4 h-4 mr-2" />
                                  Confirmer
                                </Button>
                              )}
                              {appointment.status !== 'cancelled' && !canDelete && (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => cancelAppointment(appointment.id)}
                                  className="w-full sm:w-auto min-w-[120px] border-orange-300 text-orange-600 hover:bg-orange-50 hover:border-orange-400 font-medium shadow-sm hover:shadow-md transition-all duration-200"
                                >
                                  <X className="w-4 h-4 mr-2" />
                                  Annuler
                                </Button>
                              )}
                              {canDelete && (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => deleteAppointment(appointment.id)}
                                  className="w-full sm:w-auto min-w-[120px] border-red-300 text-red-600 hover:bg-red-50 hover:border-red-400 font-medium shadow-sm hover:shadow-md transition-all duration-200"
                                >
                                  <Trash2 className="w-4 h-4 mr-2" />
                                  Supprimer
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Slots Tab */}
          <TabsContent value="slots">
            <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-100 shadow-xl rounded-2xl">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-t-2xl">
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Clock className="mr-2 h-6 w-6" />
                    Créneaux ({slots.length})
                  </div>
                  <Dialog open={showSlotDialog} onOpenChange={setShowSlotDialog}>
                    <DialogTrigger asChild>
                      <Button 
                        variant="secondary" 
                        className="bg-white/20 backdrop-blur-sm hover:bg-white/30 text-white border-white/30"
                      >
                        + Ajouter un créneau
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-white/95 backdrop-blur-sm">
                      <DialogHeader>
                        <DialogTitle className="text-center text-2xl bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                          Nouveau Créneau
                        </DialogTitle>
                      </DialogHeader>
                      <form onSubmit={createSlot} className="space-y-6">
                        <div className="space-y-2">
                          <Label htmlFor="date" className="text-slate-700 font-semibold">Date</Label>
                          <Input
                            id="date"
                            type="date"
                            value={newSlot.date}
                            onChange={(e) => setNewSlot({...newSlot, date: e.target.value})}
                            required
                            className="border-slate-300 focus:border-orange-500"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="time" className="text-slate-700 font-semibold">Heure</Label>
                          <Input
                            id="time"
                            type="time"
                            value={newSlot.time}
                            onChange={(e) => setNewSlot({...newSlot, time: e.target.value})}
                            required
                            className="border-slate-300 focus:border-orange-500"
                          />
                        </div>
                        <DialogFooter className="gap-2">
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
                </CardTitle>
                <CardDescription className="text-orange-100">
                  Gérez les créneaux disponibles pour les réservations
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="grid gap-4">
                  {slots.map((slot) => (
                    <div key={slot.id} className="flex items-center justify-between p-4 border-2 border-orange-100 rounded-xl bg-gradient-to-r from-white/90 to-orange-50/50 shadow-lg">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-orange-100 to-amber-100 rounded-full flex items-center justify-center">
                          <Clock className="w-6 h-6 text-orange-500" />
                        </div>
                        <div>
                          <div className="font-semibold text-gray-900">{formatDate(slot.date)}</div>
                          <div className="text-sm text-gray-600">{formatTime(slot.start_time)} - {formatTime(slot.end_time)}</div>
                          <Badge variant={slot.is_available ? "default" : "secondary"}>
                            {slot.is_available ? "Disponible" : "Réservé"}
                          </Badge>
                        </div>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => deleteSlot(slot.id)}
                        className="border-red-200 text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Supprimer
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reviews Tab */}
          <TabsContent value="reviews">
            <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-100 shadow-xl rounded-2xl">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-t-2xl">
                <CardTitle className="flex items-center">
                  <MessageSquare className="mr-2 h-6 w-6" />
                  Avis clients ({reviews.length})
                </CardTitle>
                <CardDescription className="text-orange-100">
                  Modérez les avis de vos clients
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {reviews.map((review) => (
                    <div key={review.id} className="border-2 border-orange-100 rounded-xl p-4 bg-gradient-to-r from-white/90 to-orange-50/50 shadow-lg">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <div className="font-semibold text-gray-900">{review.user_name || 'Utilisateur inconnu'}</div>
                          <div className="flex items-center space-x-1">
                            {[...Array(5)].map((_, i) => (
                              <span key={i} className={`text-lg ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}`}>
                                ⭐
                              </span>
                            ))}
                          </div>
                        </div>
                        <Badge variant={review.status === 'approved' ? 'default' : review.status === 'pending' ? 'secondary' : 'destructive'}>
                          {review.status === 'approved' ? 'Approuvé' : review.status === 'pending' ? 'En attente' : 'Rejeté'}
                        </Badge>
                      </div>
                      <p className="text-gray-700 mb-4">{review.comment}</p>
                      {review.status === 'pending' && (
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            onClick={() => updateReviewStatus(review.id, 'approved')}
                            className="bg-green-500 hover:bg-green-600 text-white"
                          >
                            <Check className="w-4 h-4 mr-2" />
                            Approuver
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => updateReviewStatus(review.id, 'rejected')}
                            className="border-red-200 text-red-600 hover:bg-red-50"
                          >
                            <X className="w-4 h-4 mr-2" />
                            Rejeter
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;