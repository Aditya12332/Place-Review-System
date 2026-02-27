import api from './api';

export const aiService = {
  async getPlaceSummary(placeId) {
    const response = await api.get(`/ai/places/${placeId}/summary/`);
    return response.data;
  },
  
  async regenerateSummary(placeId) {
    const response = await api.post(`/ai/places/${placeId}/regenerate-summary/`);
    return response.data;
  },
  
  async getSearchSuggestions(query) {
    const response = await api.get('/ai/search-suggestions/', {
      params: { query }
    });
    return response.data;
  },
  
  async getRecommendations() {
    const response = await api.get('/ai/recommendations/');
    return response.data;
  },
  
  async askQuestion(placeId, question) {
    const response = await api.post(`/ai/places/${placeId}/ask/`, {
      question
    });
    return response.data;
  },
  
  async getRAGStats() {
    const response = await api.get('/ai/rag-stats/');
    return response.data;
  }
};