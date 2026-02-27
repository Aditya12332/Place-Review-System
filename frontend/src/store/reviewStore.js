import { create } from 'zustand';
import { reviewService } from '../services/reviewService';

export const useReviewStore = create((set) => ({
  isLoading: false,
  error: null,
  
  createReview: async (reviewData) => {
    set({ isLoading: true, error: null });
    try {
      const data = await reviewService.createReview(reviewData);
      set({ isLoading: false });
      return data;
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Failed to create review';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },
  
  voteReview: async (reviewId, voteType) => {
    try {
      const data = await reviewService.voteReview(reviewId, voteType);
      return data;
    } catch (error) {
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
}));