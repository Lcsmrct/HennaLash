import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'https://henna-lash.onrender.com';

// Instance axios optimisée
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 secondes timeout pour Render
  headers: {
    'Content-Type': 'application/json',
  }
});

// Intercepteur pour ajouter le token automatiquement
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercepteur de réponse pour gérer les erreurs de façon centralisée
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Si erreur 401, nettoyer le token
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      // Éviter une redirection infinie
      if (window.location.pathname !== '/connexion') {
        window.location.href = '/connexion';
      }
    }
    
    return Promise.reject(error);
  }
);

// Service API optimisé avec mise en cache
export const apiService = {
  // Slots
  getSlots: async (availableOnly = false) => {
    const response = await apiClient.get(`/api/slots?available_only=${availableOnly}`);
    return response.data;
  },

  // Appointments avec optimisation
  getAppointments: async () => {
    const response = await apiClient.get('/api/appointments');
    return response.data;
  },

  createAppointment: async (appointmentData) => {
    const response = await apiClient.post('/api/appointments', appointmentData);
    return response.data;
  },

  updateAppointmentStatus: async (appointmentId, status) => {
    const response = await apiClient.put(`/api/appointments/${appointmentId}/status`, { status });
    return response.data;
  },

  deleteAppointment: async (appointmentId) => {
    await apiClient.delete(`/api/appointments/${appointmentId}`);
    return true;
  },
  cancelAppointment: async (appointmentId) => {
    const response = await apiClient.put(`/api/appointments/${appointmentId}/cancel`);
    return response.data;
  },

  // Reviews avec optimisation
  getApprovedReviews: async () => {
    const response = await apiClient.get('/api/reviews?approved_only=true');
    return response.data;
  },

  getAllReviews: async () => {
    const response = await apiClient.get('/api/reviews');
    return response.data;
  },

  createReview: async (reviewData) => {
    const response = await apiClient.post('/api/reviews', reviewData);
    return response.data;
  },

  updateReviewStatus: async (reviewId, status) => {
    const response = await apiClient.put(`/api/reviews/${reviewId}`, { status });
    return response.data;
  },

  // Slots admin
  createSlot: async (slotData) => {
    const response = await apiClient.post('/api/slots', slotData);
    return response.data;
  },

  deleteSlot: async (slotId) => {
    await apiClient.delete(`/api/slots/${slotId}`);
    return true;
  },

  // Keep-alive
  ping: async () => {
    const response = await apiClient.head('/api/ping');
    return response.status === 200;
  },

  // Batch operations pour réduire les requêtes
  getDashboardData: async (userRole = 'client') => {
    if (userRole === 'admin') {
      const [appointments, slots, reviews] = await Promise.all([
        apiClient.get('/api/appointments'),
        apiClient.get('/api/slots'),
        apiClient.get('/api/reviews')
      ]);
      return {
        appointments: appointments.data,
        slots: slots.data,
        reviews: reviews.data
      };
    } else {
      const [appointments, slots] = await Promise.all([
        apiClient.get('/api/appointments'),
        apiClient.get('/api/slots?available_only=true')
      ]);
      return {
        appointments: appointments.data,
        slots: slots.data
      };
    }
  },

  // Maintenance Management
  getMaintenanceStatus: async () => {
    const response = await apiClient.get('/api/maintenance');
    return response.data;
  },

  toggleMaintenance: async (isMaintenanceMode, message = null) => {
    const response = await apiClient.post('/api/maintenance', {
      is_maintenance: isMaintenanceMode,
      message: message
    });
    return response.data;
  },

  // Password Reset
  requestPasswordReset: async (email) => {
    const response = await apiClient.post('/api/auth/password-reset/request', { email });
    return response.data;
  },

  confirmPasswordReset: async (email, code, new_password) => {
    const response = await apiClient.post('/api/auth/password-reset/confirm', {
      email,
      code,
      new_password
    });
    return response.data;
  },

  // Maintenance Mode
  getMaintenanceStatus: async () => {
    const response = await apiClient.get('/api/maintenance');
    return response.data;
  },

  toggleMaintenance: async (is_maintenance, message = '') => {
    const response = await apiClient.post('/api/maintenance', {
      is_maintenance,
      message
    });
    return response.data;
  }
};

export default apiService;