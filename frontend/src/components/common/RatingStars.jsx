import React from 'react';
import { Star, StarHalf } from 'lucide-react';

const RatingStars = ({ rating, size = 20, showNumber = true, className = '' }) => {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
  
  return (
    <div className={`flex items-center gap-1 ${className}`}>
      <div className="flex items-center text-warning">
        {[...Array(fullStars)].map((_, i) => (
          <Star key={`full-${i}`} size={size} fill="currentColor" />
        ))}
        {hasHalfStar && <StarHalf size={size} fill="currentColor" />}
        {[...Array(emptyStars)].map((_, i) => (
          <Star key={`empty-${i}`} size={size} />
        ))}
      </div>
      {showNumber && (
        <span className="text-sm font-semibold ml-1">
          {rating.toFixed(1)}
        </span>
      )}
    </div>
  );
};

export default RatingStars;