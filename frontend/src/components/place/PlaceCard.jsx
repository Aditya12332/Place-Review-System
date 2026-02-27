import React from 'react';
import { MapPin, Star, Bookmark, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import { usePlaceStore } from '../../store/placeStore';
import { getCategoryIcon } from '../../utils/helpers';
import RatingStars from '../common/RatingStars';
import toast from 'react-hot-toast';

const PlaceCard = ({ place }) => {
  const { toggleBookmark } = usePlaceStore();
  const [isBookmarked, setIsBookmarked] = React.useState(place.is_bookmarked);
  const [isBookmarking, setIsBookmarking] = React.useState(false);
  
  const handleBookmark = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    setIsBookmarking(true);
    try {
      const result = await toggleBookmark(place.id);
      setIsBookmarked(result.bookmarked);
      toast.success(result.message);
    } catch (error) {
      toast.error('Failed to update bookmark');
    } finally {
      setIsBookmarking(false);
    }
  };
  
  return (
    <Link to={`/place/${place.id}`}>
      <div className="card bg-base-100 shadow-lg border border-base-content/10 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 h-full">
        {/* Image */}
        <figure className="relative h-48 bg-base-200">
          {place.primary_photo?.image_url ? (
            <img
              src={place.primary_photo.image_url}
              alt={place.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-6xl">
              {place.category ? getCategoryIcon(place.category.name) : '📍'}
            </div>
          )}
          
          {/* Bookmark button */}
          <button
            onClick={handleBookmark}
            disabled={isBookmarking}
            className={`absolute top-3 right-3 btn btn-circle btn-sm ${
              isBookmarked ? 'btn-primary' : 'btn-ghost bg-base-100/80'
            } shadow-lg`}
          >
            <Bookmark
              size={16}
              fill={isBookmarked ? 'currentColor' : 'none'}
            />
          </button>
          
          {/* Category badge */}
          {place.category && (
            <div className="absolute top-3 left-3 badge badge-primary gap-1 shadow-lg">
              {getCategoryIcon(place.category.name)}
              <span className="font-semibold">{place.category.name}</span>
            </div>
          )}
        </figure>
        
        <div className="card-body p-5">
          {/* Name */}
          <h3 className="card-title text-lg line-clamp-2 mb-2">
            {place.name}
          </h3>
          
          {/* Address */}
          <p className="text-sm text-base-content/70 flex items-start gap-2 line-clamp-2 mb-3">
            <MapPin size={16} className="mt-0.5 flex-shrink-0" />
            <span>{place.address}</span>
          </p>
          
          {/* Rating and stats */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <RatingStars rating={place.average_rating} size={18} />
              <span className="text-sm text-base-content/70">
                ({place.total_reviews} {place.total_reviews === 1 ? 'review' : 'reviews'})
              </span>
            </div>
            
            {place.view_count > 0 && (
              <div className="flex items-center gap-1 text-xs text-base-content/60">
                <Eye size={14} />
                <span>{place.view_count}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
};

export default PlaceCard;