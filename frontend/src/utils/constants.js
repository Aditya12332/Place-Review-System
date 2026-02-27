export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const RATING_LABELS = {
  1: 'Poor',
  2: 'Fair',
  3: 'Good',
  4: 'Very Good',
  5: 'Excellent'
};

export const SENTIMENT_COLORS = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#6b7280'
};

export const CATEGORY_ICONS = {
  'Restaurant': '🍽️',
  'Cafe': '☕',
  'Shop': '🛍️',
  'Doctor': '🏥',
  'Dentist': '🦷',
  'Gym': '💪',
  'Salon': '💇',
  'Bakery': '🍰',
  'Bar': '🍺',
  'Hotel': '🏨',
  'Default': '📍'
};

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  SEARCH: '/search',
  PLACE_DETAIL: '/place/:id',
  DASHBOARD: '/dashboard',
  BOOKMARKS: '/bookmarks',
};