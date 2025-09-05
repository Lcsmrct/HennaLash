import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
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
  const [appointments, setAppointments] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  // Redirect if not authenticated or is admin
  if (!isAuthenticated) {
    return <Navigate to="/connexion" replace />;
  }

  if (user?.role === 'admin') {
    return <Navigate to="/admin" replace />;
  }

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [appointmentsRes, slotsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/appointments`),
        axios.get(`${API_BASE_URL}/api/slots?available_only=true`)
      ]);
      
      setAppointments(appointmentsRes.data);
      setAvailableSlots(slotsRes.data);
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

  const bookAppointment = async (slotId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/appointments`, {
        slot_id: slotId
      });
      
      toast({
        title: "Succès",
        description: "Rendez-vous réservé avec succès !"
      });
      
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Error booking appointment:', error);
      toast({
        title: "Erreur",
        description: error.response?.data?.detail || "Impossible de réserver le rendez-vous",
        variant: "destructive"
      });
    }
  };

  const submitReview = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/api/reviews`, reviewForm);
      
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
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Bonjour, {user?.first_name} !
            </h1>
            <p className="text-gray-600">Gérez vos rendez-vous et laissez des avis</p>
          </div>
          <Button onClick={logout} variant="outline">
            <LogOut className="mr-2 h-4 w-4" />
            Déconnexion
          </Button>
        </div>

        <Tabs defaultValue="appointments" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="appointments">Mes Rendez-vous</TabsTrigger>
            <TabsTrigger value="booking">Réserver</TabsTrigger>
            <TabsTrigger value="reviews">Laisser un Avis</TabsTrigger>
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
                              {appointment.slot_info?.service_name || 'Service non spécifié'}
                            </h3>
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
                              <p className="text-sm text-gray-600">
                                <MessageSquare className="mr-1 h-4 w-4 inline" />
                                {appointment.notes}
                              </p>
                            )}
                          </div>
                          <div className="text-right">
                            {getStatusBadge(appointment.status)}
                            {appointment.slot_info && (
                              <p className="text-lg font-semibold mt-2">
                                {appointment.slot_info.price}€
                              </p>
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
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {availableSlots.map((slot) => (
                      <Card key={slot.id} className="cursor-pointer hover:shadow-md transition-shadow">
                        <CardContent className="p-4">
                          <h3 className="font-semibold mb-2">{slot.service_name}</h3>
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
                            className="w-full mt-4" 
                            onClick={() => bookAppointment(slot.id)}
                          >
                            Réserver
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
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
                  
                  <Button type="submit" className="w-full">
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