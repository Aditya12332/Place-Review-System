import api from './api';

export const reviewService = {
  async createReview(data) {
    const response = await api.post('/places/reviews/', data);
    return response.data;
  },
  
  async voteReview(reviewId, voteType) {
    const response = await api.post(`/places/reviews/${reviewId}/vote/`, {
      vote_type: voteType
    });
    return response.data;
  }
};