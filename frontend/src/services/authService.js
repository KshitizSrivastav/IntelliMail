import axios from 'axios';

// Dynamic API URL based on environment
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? process.env.REACT_APP_API_URL || 'https://intellimail-backend.onrender.com'
  : 'http://localhost:8000';

console.log('🔗 API Base URL:', API_BASE_URL);
console.log('🌍 Environment:', process.env.NODE_ENV);

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for Render cold starts
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async getGoogleAuthUrl() {
    const response = await api.get('/auth/google/url');
    return response.data;
  },

  async authenticateWithGoogle(authCode) {
    const response = await api.post('/auth/google/callback', {
      auth_code: authCode
    });
    return response.data;
  },

  async getCurrentUser(token) {
    const response = await api.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data.user;
  },

  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
    localStorage.removeItem('access_token');
  },

  async refreshToken(refreshToken) {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken
    });
    return response.data;
  }
};

export const emailService = {
  async getEmails(params = {}) {
    const response = await api.get('/emails/', { params });
    return response.data;
  },

  async getEmailDetail(emailId) {
    const response = await api.get(`/emails/${emailId}`);
    return response.data;
  },

  async getEmailThread(threadId) {
    const response = await api.get(`/emails/thread/${threadId}`);
    return response.data;
  },

  async sendEmail(emailData) {
    const response = await api.post('/emails/send', emailData);
    return response.data;
  },

  async markAsRead(emailId) {
    const response = await api.put(`/emails/${emailId}/mark-read`);
    return response.data;
  }
};

export const aiService = {
  async summarizeEmail(data) {
    const response = await api.post('/summarize/', data);
    return response.data;
  },

  async summarizeThread(threadId, maxLength = 200) {
    const response = await api.post(`/summarize/thread/${threadId}`, {
      max_length: maxLength
    });
    return response.data;
  },

  async generateReply(data) {
    const response = await api.post('/reply/generate', data);
    return response.data;
  },

  async refineReply(replyText, targetTone, instructions = null) {
    const response = await api.post('/reply/refine', {
      reply_text: replyText,
      target_tone: targetTone,
      refinement_instructions: instructions
    });
    return response.data;
  },

  async analyzeTone(text) {
    const response = await api.post('/reply/analyze-tone', {
      text: text
    });
    return response.data;
  },

  async getAvailableTones() {
    const response = await api.get('/reply/tones');
    return response.data;
  }
};

export default api;
