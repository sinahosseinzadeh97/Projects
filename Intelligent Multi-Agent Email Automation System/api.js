import axios from 'axios';

// Create axios instance with base URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Authentication
export const loginUser = async (credentials) => {
  try {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await axios.post(`${API_URL}/token`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error logging in:', error);
    throw error;
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/users/me/');
    return response.data;
  } catch (error) {
    console.error('Error getting current user:', error);
    throw error;
  }
};

// Email Management
export const getEmails = async () => {
  try {
    const response = await api.get('/emails');
    return response.data;
  } catch (error) {
    console.error('Error fetching emails:', error);
    throw error;
  }
};

export const getEmail = async (messageId) => {
  try {
    const response = await api.get(`/emails/${messageId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching email:', error);
    throw error;
  }
};

// Email Providers
export const getProviders = async () => {
  try {
    const response = await api.get('/ingestion/providers');
    return response.data;
  } catch (error) {
    console.error('Error fetching providers:', error);
    throw error;
  }
};

export const createProvider = async (provider) => {
  try {
    const response = await api.post('/ingestion/providers', provider);
    return response.data;
  } catch (error) {
    console.error('Error creating provider:', error);
    throw error;
  }
};

export const fetchEmails = async (providerId) => {
  try {
    const response = await api.post('/ingestion/fetch', { provider_id: providerId });
    return response.data;
  } catch (error) {
    console.error('Error fetching emails:', error);
    throw error;
  }
};

// Classification
export const classifyEmail = async (email) => {
  try {
    const response = await api.post('/classification/classify', email);
    return response.data;
  } catch (error) {
    console.error('Error classifying email:', error);
    throw error;
  }
};

export const getCategories = async () => {
  try {
    const response = await api.get('/classification/categories');
    return response.data;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

// Summarization
export const summarizeEmail = async (email) => {
  try {
    const response = await api.post('/summarization/summarize', email);
    return response.data;
  } catch (error) {
    console.error('Error summarizing email:', error);
    throw error;
  }
};

export const extractData = async (email) => {
  try {
    const response = await api.post('/summarization/extract', email);
    return response.data;
  } catch (error) {
    console.error('Error extracting data:', error);
    throw error;
  }
};

// Response Generation
export const generateResponse = async (email) => {
  try {
    const response = await api.post('/response/generate', email);
    return response.data;
  } catch (error) {
    console.error('Error generating response:', error);
    throw error;
  }
};

export const getTemplates = async () => {
  try {
    const response = await api.get('/response/templates');
    return response.data;
  } catch (error) {
    console.error('Error fetching templates:', error);
    throw error;
  }
};

// Integration
export const createCalendarEvent = async (email) => {
  try {
    const response = await api.post('/integration/calendar', email);
    return response.data;
  } catch (error) {
    console.error('Error creating calendar event:', error);
    throw error;
  }
};

export const runWorkflow = async (emails) => {
  try {
    const response = await api.post('/integration/workflow', emails);
    return response.data;
  } catch (error) {
    console.error('Error running workflow:', error);
    throw error;
  }
};

// Analytics
export const getEmailAnalytics = async () => {
  try {
    const response = await api.get('/analytics/emails');
    return response.data;
  } catch (error) {
    console.error('Error fetching email analytics:', error);
    throw error;
  }
};
