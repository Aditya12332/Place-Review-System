import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  MapPin, 
  Star, 
  Bookmark, 
  ArrowLeft, 
  MessageSquare,
  Sparkles 
} from 'lucide-react';
import { usePlaceStore } from '../store/placeStore';
import { useAuthStore } from '../store/authStore';
import Loading from '../components/common/Loading';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import RatingStars from '../components/common/RatingStars';
import PlaceStats from '../components/place/PlaceStats';
import PlacePhotos from '../components/place/PlacePhotos';
import ReviewList from '../components/review/ReviewList';
import ReviewForm from '../components/review/ReviewForm';
import AISummary from '../components/ai/AISummary';
import AskQuestion from '../components/ai/AskQuestion';
import { getCategoryIcon } from '../utils/helpers';
import toast from 'react-hot-toast';

const PlaceDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentPlace, getPlaceDetail, toggleBookmark, isLoading } = usePlaceStore();
  const { user } = useAuthStore();
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isBookmarking, setIsBookmarking] = useState(false);
  
  useEffect(() => {
    loadPlace();
  }, [id]);
  
  useEffect(() => {
    if (currentPlace) {
      setIsBookmarked(currentPlace.is_bookmarked);
    }
  }, [currentPlace]);
  
  const loadPlace = async () => {
    try {
      await getPlaceDetail(id);
    } catch (error) {
      toast.error('Failed to load place details');
      navigate('/search');
    }
  };
  
  const handleBookmark = async () => {
    if (!user) {
      toast.error('Please login to bookmark places');
      navigate('/login');
      return;
    }
    
    setIsBookmarking(true);
    try {
      const result = await toggleBookmark(currentPlace.id);
      setIsBookmarked(result.bookmarked);
      toast.success(result.message);
    } catch (error) {
      toast.error('Failed to update bookmark');
    } finally {
      setIsBookmarking(false);
    }
  };
  
  const handleReviewSuccess = () => {
    setShowReviewModal(false);
    loadPlace(); // Reload to get new review
  };
  
  if (isLoading || !currentPlace) {
    return <Loading fullScreen text="Loading place details..." />;
  }
  
  return (
    <div className="min-h-screen bg-base-200">
      {/* Header */}
      <div className="bg-base-100 border-b border-base-content/10">
        <div className="container mx-auto px-4 py-6">
          <button
            onClick={() => navigate(-1)}
            className="btn btn-ghost gap-2 mb-4"
          >
            <ArrowLeft size={20} />
            Back
          </button>
          
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-start gap-3 mb-3">
                {currentPlace.category && (
                  <span className="text-4xl">
                    {getCategoryIcon(currentPlace.category.name)}
                  </span>
                )}
                <div>
                  <h1 className="text-4xl font-bold mb-2">{currentPlace.name}</h1>
                  {currentPlace.category && (
                    <span className="badge badge-primary">
                      {currentPlace.category.name}
                    </span>
                  )}
                </div>
              </div>
              
              <p className="flex items-start gap-2 text-base-content/70 mb-4">
                <MapPin size={20} className="mt-0.5 flex-shrink-0" />
                <span>{currentPlace.address}</span>
              </p>
              
              <div className="flex items-center gap-4">
                <RatingStars rating={currentPlace.average_rating} size={24} />
                <span className="text-base-content/70">
                  Based on {currentPlace.total_reviews} reviews
                </span>
              </div>
            </div>
            
            <div className="flex gap-3">
              <Button
                variant={isBookmarked ? 'primary' : 'outline'}
                onClick={handleBookmark}
                isLoading={isBookmarking}
                className="gap-2"
              >
                <Bookmark size={20} fill={isBookmarked ? 'currentColor' : 'none'} />
                {isBookmarked ? 'Bookmarked' : 'Bookmark'}
              </Button>
              
              <Button
                variant="primary"
                onClick={() => {
                  if (!user) {
                    toast.error('Please login to write a review');
                    navigate('/login');
                    return;
                  }
                  setShowReviewModal(true);
                }}
                className="gap-2"
              >
                <MessageSquare size={20} />
                Write Review
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Stats */}
            <PlaceStats place={currentPlace} />
            
            {/* Photos */}
            {currentPlace.photos && currentPlace.photos.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold mb-4">Photos</h2>
                <PlacePhotos photos={currentPlace.photos} />
              </div>
            )}
            
            {/* Description */}
            {currentPlace.description && (
              <div className="card bg-base-100 shadow-lg border border-base-content/10 p-6">
                <h2 className="text-2xl font-bold mb-4">About</h2>
                <p className="text-base-content/80 leading-relaxed whitespace-pre-wrap">
                  {currentPlace.description}
                </p>
              </div>
            )}
            
            {/* AI Summary */}
            <AISummary placeId={currentPlace.id} />
            
            {/* Ask AI */}
            <AskQuestion placeId={currentPlace.id} />
            
            {/* Reviews */}
            <div>
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <MessageSquare />
                Reviews ({currentPlace.total_reviews})
              </h2>
              
              {/* Rating Distribution */}
              {currentPlace.rating_distribution && (
                <div className="card bg-base-100 shadow-lg border border-base-content/10 p-6 mb-6">
                  <h3 className="font-semibold mb-4">Rating Distribution</h3>
                  <div className="space-y-2">
                    {[5, 4, 3, 2, 1].map((rating) => {
                      const count = currentPlace.rating_distribution[rating.toString()] || 0;
                      const percentage = currentPlace.total_reviews > 0
                        ? (count / currentPlace.total_reviews) * 100
                        : 0;
                      
                      return (
                        <div key={rating} className="flex items-center gap-3">
                          <div className="flex items-center gap-1 w-20">
                            <span className="text-sm font-semibold">{rating}</span>
                            <Star size={14} className="text-warning" fill="currentColor" />
                          </div>
                          <progress
                            className="progress progress-warning flex-1"
                            value={percentage}
                            max="100"
                          ></progress>
                          <span className="text-sm text-base-content/70 w-12 text-right">
                            {count}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              
              <ReviewList
                reviews={currentPlace.reviews || []}
                currentUserId={user?.id}
              />
            </div>
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Info Card */}
            <div className="card bg-base-100 shadow-lg border border-base-content/10 sticky top-4">
              <div className="card-body">
                <h3 className="font-bold text-lg mb-4">Quick Info</h3>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-base-content/70">Average Rating</span>
                    <div className="flex items-center gap-2">
                      <Star size={16} className="text-warning" fill="currentColor" />
                      <span className="font-semibold">
                        {currentPlace.average_rating.toFixed(1)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="divider my-2"></div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-base-content/70">Total Reviews</span>
                    <span className="font-semibold">{currentPlace.total_reviews}</span>
                  </div>
                  
                  <div className="divider my-2"></div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-base-content/70">Views</span>
                    <span className="font-semibold">{currentPlace.view_count}</span>
                  </div>
                  
                  <div className="divider my-2"></div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-base-content/70">Category</span>
                    <span className="font-semibold">
                      {currentPlace.category?.name || 'General'}
                    </span>
                  </div>
                </div>
                
                <div className="divider"></div>
                
                <Button
                  variant="primary"
                  fullWidth
                  onClick={() => setShowReviewModal(true)}
                  className="gap-2"
                >
                  <Sparkles size={20} />
                  Share Your Experience
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Review Modal */}
      <Modal
        isOpen={showReviewModal}
        onClose={() => setShowReviewModal(false)}
        title="Write a Review"
        size="lg"
      >
        <ReviewForm
          placeName={currentPlace.name}
          placeAddress={currentPlace.address}
          categoryId={currentPlace.category?.id}
          onSuccess={handleReviewSuccess}
        />
      </Modal>
    </div>
  );
};

export default PlaceDetails;