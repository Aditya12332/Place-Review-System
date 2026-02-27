import React from 'react';
import { MessageSquare } from 'lucide-react';
import ReviewCard from './ReviewCard';
import EmptyState from '../common/EmptyState';

const ReviewList = ({ reviews = [], currentUserId }) => {
  if (reviews.length === 0) {
    return (
      <EmptyState
        icon={MessageSquare}
        title="No reviews yet"
        description="Be the first to share your experience!"
      />
    );
  }
  
  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <ReviewCard
          key={review.id}
          review={review}
          isCurrentUser={review.user.id === currentUserId}
        />
      ))}
    </div>
  );
};

export default ReviewList;