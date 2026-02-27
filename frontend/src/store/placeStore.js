import { create } from 'zustand';
import { placeService } from '../services/placeService';

export const usePlaceStore = create((set, get) => ({
  places: [],
  currentPlace: null,
  categories: [],
  searchResults: [],
  trendingPlaces: [],
  bookmarks: [],
  isLoading: false,
  error: null,
  
  // Search
  searchPlaces: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const data = await placeService.searchPlaces(params);
      set({ searchResults: data.results, isLoading: false });
      return data;
    } catch (error) {
      set({ error: 'Search failed', isLoading: false });
      throw error;
    }
  },
  
  // Get place detail
  getPlaceDetail: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const data = await placeService.getPlaceDetail(id);
      set({ currentPlace: data, isLoading: false });
      return data;
    } catch (error) {
      set({ error: 'Failed to load place', isLoading: false });
      throw error;
    }
  },
  
  // Get trending
  getTrendingPlaces: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await placeService.getTrendingPlaces();
      set({ trendingPlaces: data.results, isLoading: false });
      return data;
    } catch (error) {
      set({ error: 'Failed to load trending places', isLoading: false });
      throw error;
    }
  },
  
  // Get categories
  getCategories: async () => {
    try {
      const data = await placeService.getCategories();
      set({ categories: data });
      return data;
    } catch (error) {
      console.error('Failed to load categories', error);
    }
  },
  
  // Toggle bookmark
  toggleBookmark: async (placeId) => {
    try {
      const data = await placeService.toggleBookmark(placeId);
      
      // Update current place if viewing it
      const { currentPlace } = get();
      if (currentPlace?.id === placeId) {
        set({
          currentPlace: {
            ...currentPlace,
            is_bookmarked: data.bookmarked
          }
        });
      }
      
      return data;
    } catch (error) {
      throw error;
    }
  },
  
  // Get bookmarks
  getUserBookmarks: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await placeService.getUserBookmarks();
      set({ bookmarks: data.results, isLoading: false });
      return data;
    } catch (error) {
      set({ error: 'Failed to load bookmarks', isLoading: false });
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
}));