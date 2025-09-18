import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { AlertTriangle, Settings, Shield, ArrowLeft, Power, Zap, User } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import apiService from '../services/apiService';
import LoadingSpinner from '../components/LoadingSpinner';

const MaintenancePage = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [maintenanceStatus, setMaintenanceStatus] = useState({
    is_maintenance: false,
    message: '',
    enabled_at: null,
    enabled_by: null
  });
  const [customMessage, setCustomMessage] = useState('');

  useEffect(() => {
    // Vérifier si l'utilisateur est admin
    if (!isAuthenticated || user?.role !== 'admin') {
      navigate('/connexion');
      return;
    }
    fetchMaintenanceStatus();
  }, [isAuthenticated, user, navigate]);

  const fetchMaintenanceStatus = async () => {
    try {
      setLoading(true);
      const status = await apiService.getMaintenanceStatus();
      setMaintenanceStatus(status);
      setCustomMessage(status.message || '');
    } catch (error) {
      console.error('Error fetching maintenance status:', error);
      toast({
        title: "Erreur",
        description: "Impossible de charger le statut de maintenance",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleMaintenance = async (enabled) => {
    try {
      const message = customMessage || 'Site en maintenance. Veuillez réessayer plus tard.';
      const response = await apiService.toggleMaintenance(enabled, message);
      
      setMaintenanceStatus(response);
      
      toast({
        title: enabled ? "Mode maintenance activé" : "Mode maintenance désactivé",
        description: enabled ? 
          "Le site est maintenant en mode maintenance. Seuls les admins peuvent se connecter." :
          "Le site est maintenant accessible à tous les utilisateurs.",
        variant: enabled ? "destructive" : "default"
      });
    } catch (error) {
      console.error('Error toggling maintenance:', error);
      toast({
        title: "Erreur",
        description: "Impossible de modifier le mode maintenance",
        variant: "destructive"
      });
    }
  };

  const goBack = () => {
    navigate('/admin');
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!isAuthenticated || user?.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-50">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <Shield className="w-16 h-16 mx-auto text-red-500 mb-4" />
            <CardTitle className="text-red-600">Accès non autorisé</CardTitle>
            <CardDescription>Cette page est réservée aux administrateurs</CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-100">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 shadow-2xl border-2 border-orange-200 max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-2xl flex items-center justify-center mr-4 shadow-lg">
                <Settings className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-4xl sm:text-5xl font-bold">
                <span className="bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  Mode Maintenance
                </span>
              </h1>
            </div>
            <p className="text-gray-700 text-lg sm:text-xl font-medium mb-6">
              Contrôlez l'accès au site et gérez les périodes de maintenance
            </p>
            
            {/* Navigation */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                onClick={goBack}
                variant="outline"
                size="lg"
                className="w-full sm:w-auto min-w-[180px] bg-white/80 backdrop-blur-sm border-2 border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
              >
                <ArrowLeft className="mr-2 h-5 w-5" />
                Retour Admin
              </Button>
              
              <Button 
                onClick={handleLogout}
                variant="outline"
                size="lg"
                className="w-full sm:w-auto min-w-[180px] bg-white/80 backdrop-blur-sm border-2 border-orange-300 text-orange-700 hover:bg-orange-50 hover:border-orange-400 font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
              >
                <User className="mr-2 h-5 w-5" />
                Se déconnecter
              </Button>
            </div>
          </div>
        </div>

        {/* Status Card */}
        <div className="max-w-4xl mx-auto mb-8">
          <Card className="bg-white/90 backdrop-blur-sm border-2 shadow-2xl rounded-2xl overflow-hidden">
            <CardHeader className={`transition-all duration-500 ${
              maintenanceStatus.is_maintenance 
                ? 'bg-gradient-to-r from-red-500 to-rose-500 text-white' 
                : 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
            }`}>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  {maintenanceStatus.is_maintenance ? (
                    <AlertTriangle className="mr-3 h-8 w-8" />
                  ) : (
                    <Zap className="mr-3 h-8 w-8" />
                  )}
                  <span className="text-2xl font-bold">
                    Statut: {maintenanceStatus.is_maintenance ? 'MAINTENANCE ACTIVE' : 'SITE OPÉRATIONNEL'}
                  </span>
                </div>
                <Badge 
                  variant={maintenanceStatus.is_maintenance ? "destructive" : "default"}
                  className="text-lg px-4 py-2 font-bold"
                >
                  {maintenanceStatus.is_maintenance ? '🚨 MAINTENANCE' : '✅ ACTIF'}
                </Badge>
              </CardTitle>
              <CardDescription className={`text-lg font-medium ${
                maintenanceStatus.is_maintenance ? 'text-red-100' : 'text-green-100'
              }`}>
                Seuls les administrateurs peuvent se connecter en mode maintenance
              </CardDescription>
            </CardHeader>
            <CardContent className="p-8">
              {/* Informations détaillées */}
              {maintenanceStatus.is_maintenance && (
                <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 mb-6">
                  <h3 className="font-bold text-red-800 mb-3 flex items-center">
                    <AlertTriangle className="w-5 h-5 mr-2" />
                    Maintenance en cours
                  </h3>
                  <div className="space-y-2 text-red-700">
                    {maintenanceStatus.enabled_at && (
                      <p><strong>Activée le:</strong> {new Date(maintenanceStatus.enabled_at).toLocaleString('fr-FR')}</p>
                    )}
                    {maintenanceStatus.enabled_by && (
                      <p><strong>Activée par:</strong> Admin ID {maintenanceStatus.enabled_by}</p>
                    )}
                    <p><strong>Message affiché:</strong> "{maintenanceStatus.message}"</p>
                  </div>
                </div>
              )}

              {/* Configuration du message */}
              <div className="space-y-6">
                <div>
                  <Label htmlFor="message" className="text-lg font-semibold text-gray-800 mb-3 block">
                    Message de maintenance personnalisé
                  </Label>
                  <Textarea
                    id="message"
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    placeholder="Saisissez le message qui sera affiché aux utilisateurs pendant la maintenance..."
                    className="min-h-[120px] text-base border-2 border-gray-300 rounded-xl focus:border-purple-500 transition-all duration-300"
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Ce message sera affiché sur la page d'accueil pendant la maintenance
                  </p>
                </div>

                {/* Toggle maintenance */}
                <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 border-2 border-purple-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-gray-800 mb-2 flex items-center">
                        <Power className="w-6 h-6 mr-2 text-purple-600" />
                        Activer/Désactiver la maintenance
                      </h3>
                      <p className="text-gray-600">
                        {maintenanceStatus.is_maintenance 
                          ? 'Le site est actuellement inaccessible aux utilisateurs normaux'
                          : 'Le site est actuellement accessible à tous les utilisateurs'
                        }
                      </p>
                    </div>
                    <div className="flex flex-col items-center">
                      <Switch
                        checked={maintenanceStatus.is_maintenance}
                        onCheckedChange={toggleMaintenance}
                        className="mb-2 scale-150"
                      />
                      <span className="text-sm font-medium text-gray-600">
                        {maintenanceStatus.is_maintenance ? 'ON' : 'OFF'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions rapides */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button
                    onClick={() => toggleMaintenance(true)}
                    disabled={maintenanceStatus.is_maintenance}
                    size="lg"
                    className="w-full bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 text-white font-bold py-4 shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
                  >
                    <AlertTriangle className="w-5 h-5 mr-2" />
                    Activer la maintenance
                  </Button>
                  
                  <Button
                    onClick={() => toggleMaintenance(false)}
                    disabled={!maintenanceStatus.is_maintenance}
                    size="lg"
                    variant="outline"
                    className="w-full border-2 border-green-400 text-green-700 hover:bg-green-50 hover:border-green-500 font-bold py-4 shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
                  >
                    <Zap className="w-5 h-5 mr-2" />
                    Désactiver la maintenance
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Informations importantes */}
        <div className="max-w-4xl mx-auto">
          <Card className="bg-blue-50 border-2 border-blue-200 shadow-xl rounded-2xl">
            <CardHeader className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-t-2xl">
              <CardTitle className="flex items-center">
                <Shield className="mr-2 h-6 w-6" />
                Informations importantes
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4 text-blue-800">
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-3 mt-2 flex-shrink-0"></div>
                  <p><strong>Accès administrateur:</strong> Les administrateurs peuvent toujours se connecter, même en mode maintenance</p>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-3 mt-2 flex-shrink-0"></div>
                  <p><strong>Utilisateurs normaux:</strong> Seront redirigés vers une page de maintenance avec votre message personnalisé</p>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-3 mt-2 flex-shrink-0"></div>
                  <p><strong>Sécurité:</strong> Utilisez cette fonctionnalité pour les mises à jour, corrections ou maintenance planifiée</p>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-3 mt-2 flex-shrink-0"></div>
                  <p><strong>N'oubliez pas:</strong> Désactivez le mode maintenance une fois vos interventions terminées</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MaintenancePage;