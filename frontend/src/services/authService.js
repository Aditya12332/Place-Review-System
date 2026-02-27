import api from './api';

export const authService = {
  async register(data) {
    const response = await api.post('/users/register/', data);
    return response.data;
  },
  
  async login(data) {
    const response = await api.post('/users/login/', data);
    const { user, tokens } = response.data;
    
    // Store tokens and user
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  },
  
  async getProfile() {
    const response = await api.get('/users/profile/');
    return response.data;
  },
  
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
  
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
};