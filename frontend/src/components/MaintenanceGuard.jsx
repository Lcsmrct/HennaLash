import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/apiService';
import { AlertTriangle, Settings, User } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

const MaintenanceGuard = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [maintenanceStatus, setMaintenanceStatus] = useState({
    is_maintenance: false,
    message: '',
    enabled_at: null,
    enabled_by: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkMaintenanceStatus();
  }, []);

  const checkMaintenanceStatus = async () => {
    try {
      const status = await apiService.getMaintenanceStatus();
      setMaintenanceStatus(status);
    } catch (error) {
      console.error('Error checking maintenance status:', error);
      // En cas d'erreur, on considère que le site n'est pas en maintenance
      setMaintenanceStatus({
        is_maintenance: false,
        message: '',
        enabled_at: null,
        enabled_by: null
      });
    } finally {
      setLoading(false);
    }
  };

  // Si en cours de vérification de maintenance, afficher un loading léger
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Vérification du statut...</p>
        </div>
      </div>
    );
  }

  // Si le site est en maintenance ET l'utilisateur n'est pas admin
  if (maintenanceStatus.is_maintenance && (!isAuthenticated || user?.role !== 'admin')) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-rose-50 flex items-center justify-center px-4">
        <div className="max-w-2xl mx-auto text-center">
          <Card className="bg-white/90 backdrop-blur-sm border-2 border-orange-200 shadow-2xl rounded-3xl overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white p-8">
              <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-10 h-10 text-white" />
              </div>
              <CardTitle className="text-3xl font-bold mb-2">Site en Maintenance</CardTitle>
              <CardDescription className="text-orange-100 text-lg font-medium">
                Nous effectuons actuellement des améliorations sur notre site
              </CardDescription>
            </CardHeader>
            <CardContent className="p-8">
              <div className="space-y-6">
                <div className="bg-orange-50 border-2 border-orange-200 rounded-xl p-6">
                  <h3 className="font-bold text-orange-800 mb-3 flex items-center justify-center">
                    <Settings className="w-5 h-5 mr-2" />
                    Message de l'équipe
                  </h3>
                  <p className="text-orange-700 text-lg text-center leading-relaxed">
                    {maintenanceStatus.message || 'Site en maintenance. Veuillez réessayer plus tard.'}
                  </p>
                </div>

                <div className="space-y-4">
                  <p className="text-gray-600 text-center">
                    Nous vous remercions pour votre patience et nous excusons pour ce désagrément temporaire.
                  </p>
                  
                  <div className="flex items-center justify-center text-sm text-gray-500">
                    <span>💙 L'équipe HennaLash</span>
                  </div>
                </div>

                {/* Section admin login pour les admins */}
                <div className="border-t-2 border-gray-200 pt-6">
                  <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
                    <div className="flex items-center justify-center">
                      <User className="w-5 h-5 mr-2 text-blue-600" />
                      <span className="text-blue-700 font-medium">Vous êtes administrateur ?</span>
                    </div>
                    <div className="mt-3 text-center">
                      <Button 
                        onClick={() => window.location.href = '/connexion'}
                        className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white font-semibold px-6 py-2 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                      >
                        Connexion Admin
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Site normal ou utilisateur admin
  return children;
};

export default MaintenanceGuard;