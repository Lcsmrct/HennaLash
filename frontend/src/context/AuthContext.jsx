import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));

  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          // Vérifier d'abord le cache utilisateur
          const cachedUser = localStorage.getItem('cached_user');
          const cacheTimestamp = localStorage.getItem('user_cache_timestamp');
          const now = Date.now();
          
          // Si on a un cache valide (moins de 10 minutes), l'utiliser
          if (cachedUser && cacheTimestamp && (now - parseInt(cacheTimestamp)) < 10 * 60 * 1000) {
            setUser(JSON.parse(cachedUser));
            setLoading(false);
            return;
          }
          
          const response = await axios.get(`${API_BASE_URL}/api/auth/me`);
          const userData = response.data;
          setUser(userData);
          
          // Mettre en cache les données utilisateur
          localStorage.setItem('cached_user', JSON.stringify(userData));
          localStorage.setItem('user_cache_timestamp', now.toString());
          
        } catch (error) {
          console.error('Auth check failed:', error);
          // Token might be expired
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token, API_BASE_URL]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password
      });

      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('auth_token', access_token);

      // Get user info
      const userResponse = await axios.get(`${API_BASE_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      setUser(userResponse.data);
      
      // Mettre en cache les données utilisateur après login
      const now = Date.now();
      localStorage.setItem('cached_user', JSON.stringify(userResponse.data));
      localStorage.setItem('user_cache_timestamp', now.toString());
      
      return { success: true, user: userResponse.data };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, userData);
      return { success: true, user: response.data };
    } catch (error) {
      console.error('Registration failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('cached_user');
    localStorage.removeItem('user_cache_timestamp');
    delete axios.defaults.headers.common['Authorization'];
    // Redirect to home page after logout
    window.location.href = '/';
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};