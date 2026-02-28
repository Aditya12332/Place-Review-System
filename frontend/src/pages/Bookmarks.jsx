import React, { useEffect } from 'react';
import { Bookmark, BookmarkX } from 'lucide-react';
import { usePlaceStore } from '../store/placeStore';
import PlaceCard from '../components/place/PlaceCard';
import EmptyState from '../components/common/EmptyState';
import Loading from '../components/common/Loading';
import { useNavigate } from 'react-router-dom';

const Bookmarks = () => {
  const navigate = useNavigate();
  const { bookmarks, getUserBookmarks, isLoading } = usePlaceStore();
  
  useEffect(() => {
    getUserBookmarks();
  }, []);
  
  if (isLoading) {
    return <Loading fullScreen text="Loading your bookmarks..." />;
  }
  
  return (
    <div className="min-h-screen bg-base-200">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-3 mb-2">
            <Bookmark className="text-primary" size={36} />
            My Bookmarks
          </h1>
          <p className="text-base-content/70">
            {bookmarks.length === 0 
              ? 'No bookmarked places yet'
              : `You have ${bookmarks.length} saved ${bookmarks.length === 1 ? 'place' : 'places'}`
            }
          </p>
        </div>
        
        {/* Content */}
        {bookmarks.length === 0 ? (
          <EmptyState
            icon={BookmarkX}
            title="No bookmarks yet"
            description="Start exploring and bookmark places you'd like to visit!"
            action={() => navigate('/search')}
            actionLabel="Explore Places"
          />
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {bookmarks.map((bookmark) => (
              <PlaceCard key={bookmark.id} place={bookmark.place} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Bookmarks;