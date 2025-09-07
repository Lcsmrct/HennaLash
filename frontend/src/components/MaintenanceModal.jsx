import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Toggle } from './ui/toggle';
import { Settings, AlertTriangle, Wrench } from 'lucide-react';
import { useToast } from './ui/use-toast';
import apiService from '../services/apiService';

const MaintenanceModal = ({ isAdmin = false }) => {
  const [open, setOpen] = useState(false);
  const [isMaintenanceMode, setIsMaintenanceMode] = useState(false);
  const [maintenanceMessage, setMaintenanceMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Charger le statut de maintenance au montage
  useEffect(() => {
    loadMaintenanceStatus();
  }, []);

  const loadMaintenanceStatus = async () => {
    try {
      const status = await apiService.getMaintenanceStatus();
      setIsMaintenanceMode(status.is_maintenance);
      setMaintenanceMessage(status.message || '');
    } catch (error) {
      console.error('Erreur lors du chargement du statut de maintenance:', error);
    }
  };

  const handleToggleMaintenance = async () => {
    if (!isAdmin) {
      toast({
        title: "Accès refusé",
        description: "Seuls les administrateurs peuvent modifier le mode maintenance.",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const result = await apiService.toggleMaintenance(
        !isMaintenanceMode,
        maintenanceMessage || "Site en maintenance. Veuillez réessayer plus tard."
      );
      
      setIsMaintenanceMode(result.is_maintenance);
      setMaintenanceMessage(result.message);
      
      toast({
        title: "Succès",
        description: result.is_maintenance 
          ? "Mode maintenance activé" 
          : "Mode maintenance désactivé",
        variant: result.is_maintenance ? "destructive" : "default"
      });

      // Fermer le modal après un délai
      setTimeout(() => setOpen(false), 1500);
      
    } catch (error) {
      console.error('Erreur lors de la modification du mode maintenance:', error);
      toast({
        title: "Erreur",
        description: "Impossible de modifier le mode maintenance.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMessageChange = (e) => {
    setMaintenanceMessage(e.target.value);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          variant={isMaintenanceMode ? "destructive" : "outline"} 
          size="sm"
          className={`gap-2 ${isMaintenanceMode ? 'animate-pulse' : ''}`}
        >
          {isMaintenanceMode ? (
            <>
              <AlertTriangle className="h-4 w-4" />
              Maintenance Active
            </>
          ) : (
            <>
              <Wrench className="h-4 w-4" />
              Maintenance
            </>
          )}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Mode Maintenance
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Statut actuel */}
          <div className="p-4 rounded-lg bg-muted">
            <div className="flex items-center justify-between">
              <span className="font-medium">Statut actuel:</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                isMaintenanceMode 
                  ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' 
                  : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              }`}>
                {isMaintenanceMode ? 'Maintenance Active' : 'Site Opérationnel'}
              </span>
            </div>
          </div>

          {/* Message de maintenance */}
          <div className="space-y-2">
            <Label htmlFor="maintenance-message">
              Message de maintenance
            </Label>
            <Input
              id="maintenance-message"
              value={maintenanceMessage}
              onChange={handleMessageChange}
              placeholder="Message affiché pendant la maintenance..."
              disabled={!isAdmin}
            />
          </div>

          {/* Contrôles admin */}
          {isAdmin && (
            <div className="flex items-center justify-between p-4 rounded-lg border">
              <div className="space-y-1">
                <p className="font-medium">
                  {isMaintenanceMode ? 'Désactiver' : 'Activer'} la maintenance
                </p>
                <p className="text-sm text-muted-foreground">
                  {isMaintenanceMode 
                    ? 'Le site redeviendra accessible aux clients'
                    : 'Le site sera inaccessible pour les clients'
                  }
                </p>
              </div>
              <Toggle
                pressed={!isMaintenanceMode}
                onPressedChange={() => handleToggleMaintenance()}
                disabled={loading}
                className={`data-[state=on]:bg-green-500 data-[state=off]:bg-red-500 ${
                  isMaintenanceMode ? 'bg-red-500' : 'bg-green-500'
                }`}
              >
                {isMaintenanceMode ? 'OFF' : 'ON'}
              </Toggle>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Fermer
            </Button>
            {isAdmin && (
              <Button
                onClick={handleToggleMaintenance}
                disabled={loading}
                variant={isMaintenanceMode ? "default" : "destructive"}
              >
                {loading ? (
                  "Traitement..."
                ) : isMaintenanceMode ? (
                  "Désactiver Maintenance"
                ) : (
                  "Activer Maintenance"
                )}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default MaintenanceModal;