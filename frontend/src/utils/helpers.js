export const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
};

export const formatRating = (rating) => {
  return rating ? rating.toFixed(1) : '0.0';
};

export const truncateText = (text, maxLength = 150) => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const getStarRating = (rating) => {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
  
  return {
    full: fullStars,
    half: hasHalfStar ? 1 : 0,
    empty: emptyStars
  };
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const getCategoryIcon = (categoryName) => {
  const icons = {
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
  };
  return icons[categoryName] || '📍';
};

export const getSentimentColor = (sentiment) => {
  const colors = {
    positive: 'text-success',
    negative: 'text-error',
    neutral: 'text-base-content/70'
  };
  return colors[sentiment] || colors.neutral;
};

export const getSentimentEmoji = (sentiment) => {
  const emojis = {
    positive: '😊',
    negative: '😞',
    neutral: '😐'
  };
  return emojis[sentiment] || emojis.neutral;
};