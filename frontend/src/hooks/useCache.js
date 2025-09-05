import { useState, useEffect, useCallback } from 'react';

// Cache global pour toute l'application
const cache = new Map();
const cacheTimestamps = new Map();

export const useCache = (key, fetchFn, cacheTime = 5 * 60 * 1000) => { // 5 minutes par défaut
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (forceRefresh = false) => {
    const now = Date.now();
    const cachedData = cache.get(key);
    const timestamp = cacheTimestamps.get(key);

    // Utiliser le cache si disponible et non expiré
    if (!forceRefresh && cachedData && timestamp && (now - timestamp < cacheTime)) {
      setData(cachedData);
      setLoading(false);
      return cachedData;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await fetchFn();
      
      // Mettre en cache le résultat
      cache.set(key, result);
      cacheTimestamps.set(key, now);
      
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      console.error(`Error fetching ${key}:`, err);
    } finally {
      setLoading(false);
    }
  }, [key, fetchFn, cacheTime]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const invalidateCache = useCallback(() => {
    cache.delete(key);
    cacheTimestamps.delete(key);
  }, [key]);

  const refresh = useCallback(() => {
    return fetchData(true);
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refresh,
    invalidateCache,
    refetch: fetchData
  };
};

// Fonction utilitaire pour invalider tout le cache
export const clearAllCache = () => {
  cache.clear();
  cacheTimestamps.clear();
};

// Fonction utilitaire pour keep-alive (éviter la mise en veille)
export const setupKeepAlive = (interval = 45000) => { // 45 secondes
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 
    (typeof window !== 'undefined' && window.import?.meta?.env?.REACT_APP_BACKEND_URL);
  
  if (!API_BASE_URL) return null;

  const keepAliveInterval = setInterval(async () => {
    try {
      // Ping léger au backend pour maintenir la connexion
      await fetch(`${API_BASE_URL}/api/ping`, { 
        method: 'HEAD',
        cache: 'no-cache'
      });
    } catch (error) {
      console.warn('Keep-alive ping failed:', error);
    }
  }, interval);

  return () => clearInterval(keepAliveInterval);
};