import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, User, Sparkles } from 'lucide-react';
import { formatDate, getSentimentEmoji, getSentimentColor } from '../../utils/helpers';
import { useReviewStore } from '../../store/reviewStore';
import { useAuthStore } from '../../store/authStore';
import RatingStars from '../common/RatingStars';
import toast from 'react-hot-toast';

const ReviewCard = ({ review, isCurrentUser = false }) => {
  const { voteReview } = useReviewStore();
  const { user } = useAuthStore();
  const [voteState, setVoteState] = useState({
    type: review.user_vote,
    helpfulCount: review.helpful_count,
    notHelpfulCount: review.not_helpful_count
  });
  const [isVoting, setIsVoting] = useState(false);
  
  const handleVote = async (voteType) => {
    if (!user) {
      toast.error('Please login to vote');
      return;
    }
    
    setIsVoting(true);
    try {
      const result = await voteReview(review.id, voteType);
      setVoteState({
        type: result.vote_type,
        helpfulCount: result.helpful_count,
        notHelpfulCount: result.not_helpful_count
      });
      toast.success(result.message);
    } catch (error) {
      toast.error('Failed to vote');
    } finally {
      setIsVoting(false);
    }
  };
  
  return (
    <div className={`card bg-base-100 border ${
      isCurrentUser ? 'border-primary/50 shadow-lg' : 'border-base-content/10'
    } p-6`}>
      {isCurrentUser && (
        <div className="badge badge-primary mb-4">Your Review</div>
      )}
      
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {/* User avatar */}
          <div className="avatar placeholder">
            <div className="bg-primary text-primary-content rounded-full w-10 h-10">
              <span className="text-lg font-semibold">
                {review.user.name.charAt(0).toUpperCase()}
              </span>
            </div>
          </div>
          
          {/* User info */}
          <div>
            <p className="font-semibold">{review.user.name}</p>
            <p className="text-sm text-base-content/60">
              {formatDate(review.created_at)}
            </p>
          </div>
        </div>
        
        {/* Rating */}
        <RatingStars rating={review.rating} size={18} />
      </div>
      
      {/* Review text */}
      <p className="text-base-content/90 mb-4 whitespace-pre-wrap">
        {review.text}
      </p>
      
      {/* AI Analysis */}
      {review.ai_analysis && (
        <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={16} className="text-primary" />
            <span className="text-sm font-semibold text-primary">AI Insights</span>
          </div>
          
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-base-content/70">Sentiment:</span>
              <span className={`font-semibold ${getSentimentColor(review.ai_analysis.sentiment)}`}>
                {getSentimentEmoji(review.ai_analysis.sentiment)} {review.ai_analysis.sentiment}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-base-content/70">Quality Score:</span>
              <div className="badge badge-primary">
                {(review.ai_analysis.quality_score * 100).toFixed(0)}%
              </div>
            </div>
          </div>
          
          {review.ai_analysis.keywords.length > 0 && (
            <div className="mt-3">
              <span className="text-xs text-base-content/60">Keywords: </span>
              <div className="flex flex-wrap gap-2 mt-1">
                {review.ai_analysis.keywords.map((keyword, index) => (
                  <span key={index} className="badge badge-sm badge-outline">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {review.ai_analysis.helpful_reason && (
            <p className="text-xs text-base-content/70 mt-2 italic">
              "{review.ai_analysis.helpful_reason}"
            </p>
          )}
        </div>
      )}
      
      {/* Voting */}
      {!isCurrentUser && (
        <div className="flex items-center gap-3 pt-4 border-t border-base-content/10">
          <span className="text-sm text-base-content/70">Was this helpful?</span>
          
          <button
            onClick={() => handleVote('helpful')}
            disabled={isVoting}
            className={`btn btn-sm gap-2 ${
              voteState.type === 'helpful' ? 'btn-success' : 'btn-ghost'
            }`}
          >
            <ThumbsUp size={16} />
            <span>{voteState.helpfulCount}</span>
          </button>
          
          <button
            onClick={() => handleVote('not_helpful')}
            disabled={isVoting}
            className={`btn btn-sm gap-2 ${
              voteState.type === 'not_helpful' ? 'btn-error' : 'btn-ghost'
            }`}
          >
            <ThumbsDown size={16} />
            <span>{voteState.notHelpfulCount}</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default ReviewCard;