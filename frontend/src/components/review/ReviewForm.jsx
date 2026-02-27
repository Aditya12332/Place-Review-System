import React, { useState } from 'react';
import { Star } from 'lucide-react';
import { useReviewStore } from '../../store/reviewStore';
import Button from '../common/Button';
import Input from '../common/Input';
import toast from 'react-hot-toast';
import { RATING_LABELS } from '../../utils/constants';

const ReviewForm = ({ placeName, placeAddress, categoryId, onSuccess }) => {
  const { createReview, isLoading } = useReviewStore();
  const [formData, setFormData] = useState({
    rating: 0,
    text: ''
  });
  const [hoveredRating, setHoveredRating] = useState(0);
  
  const handleRatingClick = (rating) => {
    setFormData(prev => ({ ...prev, rating }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.rating === 0) {
      toast.error('Please select a rating');
      return;
    }
    
    if (!formData.text.trim()) {
      toast.error('Please write a review');
      return;
    }
    
    try {
      await createReview({
        place_name: placeName,
        place_address: placeAddress,
        category_id: categoryId,
        rating: formData.rating,
        text: formData.text
      });
      
      toast.success('Review posted successfully!');
      setFormData({ rating: 0, text: '' });
      onSuccess?.();
    } catch (error) {
      toast.error('Failed to post review');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Rating Selection */}
      <div>
        <label className="label">
          <span className="label-text font-semibold text-lg">Your Rating</span>
        </label>
        
        <div className="flex items-center gap-2 mb-2">
          {[1, 2, 3, 4, 5].map((rating) => (
            <button
              key={rating}
              type="button"
              onClick={() => handleRatingClick(rating)}
              onMouseEnter={() => setHoveredRating(rating)}
              onMouseLeave={() => setHoveredRating(0)}
              className="btn btn-ghost btn-lg p-2 hover:scale-110 transition-transform"
            >
              <Star
                size={32}
                fill={
                  rating <= (hoveredRating || formData.rating)
                    ? '#facc15'
                    : 'none'
                }
                className={
                  rating <= (hoveredRating || formData.rating)
                    ? 'text-warning'
                    : 'text-base-content/30'
                }
              />
            </button>
          ))}
        </div>
        
        {formData.rating > 0 && (
          <p className="text-sm text-primary font-semibold">
            {RATING_LABELS[formData.rating]}
          </p>
        )}
      </div>
      
      {/* Review Text */}
      <div>
        <label className="label">
          <span className="label-text font-semibold text-lg">Your Review</span>
        </label>
        <textarea
          value={formData.text}
          onChange={(e) => setFormData(prev => ({ ...prev, text: e.target.value }))}
          placeholder="Share your experience... What did you like? What could be improved?"
          className="textarea textarea-bordered w-full h-32 text-base"
          required
        />
        <label className="label">
          <span className="label-text-alt">
            {formData.text.length} characters
          </span>
        </label>
      </div>
      
      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        isLoading={isLoading}
      >
        Post Review
      </Button>
    </form>
  );
};

export default ReviewForm;