import { useState, useEffect } from 'react';
import apiService from '../services/apiService';

export const useMaintenance = () => {
  const [maintenanceStatus, setMaintenanceStatus] = useState({
    is_maintenance: false,
    message: '',
    enabled_at: null,
    enabled_by: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkMaintenanceStatus = async () => {
    try {
      setLoading(true);
      const status = await apiService.getMaintenanceStatus();
      setMaintenanceStatus(status);
      setError(null);
    } catch (err) {
      console.error('Erreur lors de la vérification du statut de maintenance:', err);
      setError(err);
      // En cas d'erreur API, on assume que le site n'est pas en maintenance
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

  useEffect(() => {
    checkMaintenanceStatus();
    
    // Vérification de maintenance désactivée pour éviter l'auto-refresh
    // const interval = setInterval(checkMaintenanceStatus, 30000);
    // return () => clearInterval(interval);
  }, []);

  return {
    maintenanceStatus,
    loading,
    error,
    refetch: checkMaintenanceStatus
  };
};