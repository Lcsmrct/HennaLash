import React from 'react';
import { AlertTriangle, Clock, Wrench } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';

const MaintenancePage = ({ maintenanceInfo = null }) => {
  const defaultMessage = "Site en maintenance. Veuillez réessayer plus tard.";
  const message = maintenanceInfo?.message || defaultMessage;
  const enabledAt = maintenanceInfo?.enabled_at;

  const handleRefresh = () => {
    window.location.reload();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-pink-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <Card className="text-center shadow-lg">
          <CardHeader className="pb-4">
            <div className="mx-auto w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
              <Wrench className="h-8 w-8 text-orange-600" />
            </div>
            <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
              Maintenance en cours
            </CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="text-left">
                  <p className="text-yellow-800 font-medium mb-1">
                    Service temporairement indisponible
                  </p>
                  <p className="text-yellow-700 text-sm">
                    {message}
                  </p>
                </div>
              </div>
            </div>

            {enabledAt && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-2 justify-center text-blue-700">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm">
                    Maintenance démarrée le {formatDate(enabledAt)}
                  </span>
                </div>
              </div>
            )}

            <div className="space-y-3">
              <p className="text-gray-600 text-sm">
                Nous effectuons actuellement des améliorations sur notre site. 
                Nous serons de retour très bientôt !
              </p>
              
              <Button 
                onClick={handleRefresh} 
                className="w-full"
                variant="outline"
              >
                Actualiser la page
              </Button>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                En cas d'urgence, vous pouvez nous contacter directement.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MaintenancePage;