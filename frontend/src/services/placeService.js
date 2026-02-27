import api from './api';

export const placeService = {
  async searchPlaces(params) {
    const response = await api.get('/places/search/', { params });
    return response.data;
  },
  
  async getPlaceDetail(id) {
    const response = await api.get(`/places/${id}/`);
    return response.data;
  },
  
  async getTrendingPlaces() {
    const response = await api.get('/places/trending/');
    return response.data;
  },
  
  async getCategories() {
    const response = await api.get('/places/categories/');
    return response.data;
  },
  
  async toggleBookmark(placeId) {
    const response = await api.post(`/places/${placeId}/bookmark/`);
    return response.data;
  },
  
  async getUserBookmarks() {
    const response = await api.get('/places/bookmarks/');
    return response.data;
  },
  
  async getStats() {
    const response = await api.get('/places/stats/');
    return response.data;
  }
};