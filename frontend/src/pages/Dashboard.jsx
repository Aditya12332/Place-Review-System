import React, { useEffect, useState } from 'react';
import { 
  User, 
  Star, 
  MessageSquare, 
  Bookmark, 
  TrendingUp,
  Calendar,
  Award
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { usePlaceStore } from '../store/placeStore';
import Recommendations from '../components/ai/Recommendations';
import PlaceCard from '../components/place/PlaceCard';
import Loading from '../components/common/Loading';
import { formatDate } from '../utils/helpers';
import { reviewService } from '../services/reviewService';
import Card from '../components/common/Card';

const Dashboard = () => {
  const { user } = useAuthStore();
  const { getUserBookmarks, bookmarks } = usePlaceStore();
  const [userStats, setUserStats] = useState(null);
  const [recentReviews, setRecentReviews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Load bookmarks
      await getUserBookmarks();
      
      // Load user stats (you can create a dedicated endpoint for this)
      // For now, we'll mock it
      setUserStats({
        totalReviews: 12,
        averageRating: 4.2,
        placesVisited: 8,
        memberSince: user.date_joined || '2024-01-01'
      });
      
      // Recent reviews would come from an API endpoint
      // For now, empty array
      setRecentReviews([]);
      
    } catch (error) {
      console.error('Failed to load dashboard data', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return <Loading fullScreen text="Loading your dashboard..." />;
  }
  
  return (
    <div className="min-h-screen bg-base-200">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-2">
            <div className="avatar placeholder">
              <div className="bg-primary text-primary-content rounded-full w-16">
                <span className="text-3xl font-bold">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold">Welcome back, {user.name}!</h1>
              <p className="text-base-content/70">Here's your activity overview</p>
            </div>
          </div>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Reviews */}
          <Card hover className="stats shadow">
            <div className="stat">
              <div className="stat-figure text-primary">
                <MessageSquare size={32} />
              </div>
              <div className="stat-title">Total Reviews</div>
              <div className="stat-value text-primary">{userStats.totalReviews}</div>
              <div className="stat-desc">Keep sharing your experiences!</div>
            </div>
          </Card>
          
          {/* Average Rating Given */}
          <Card hover className="stats shadow">
            <div className="stat">
              <div className="stat-figure text-secondary">
                <Star size={32} />
              </div>
              <div className="stat-title">Avg Rating Given</div>
              <div className="stat-value text-secondary">{userStats.averageRating}</div>
              <div className="stat-desc">You're a generous reviewer</div>
            </div>
          </Card>
          
          {/* Places Visited */}
          <Card hover className="stats shadow">
            <div className="stat">
              <div className="stat-figure text-accent">
                <Award size={32} />
              </div>
              <div className="stat-title">Places Visited</div>
              <div className="stat-value text-accent">{userStats.placesVisited}</div>
              <div className="stat-desc">Explore more!</div>
            </div>
          </Card>
          
          {/* Bookmarks */}
          <Card hover className="stats shadow">
            <div className="stat">
              <div className="stat-figure text-info">
                <Bookmark size={32} />
              </div>
              <div className="stat-title">Bookmarks</div>
              <div className="stat-value text-info">{bookmarks.length}</div>
              <div className="stat-desc">Saved places</div>
            </div>
          </Card>
        </div>
        
        {/* AI Recommendations */}
        <div className="mb-8">
          <Recommendations />
        </div>
        
        {/* Two Column Layout */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Recent Activity */}
          <Card>
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <TrendingUp className="text-primary" />
              Recent Activity
            </h2>
            
            {recentReviews.length === 0 ? (
              <div className="text-center py-12">
                <MessageSquare size={48} className="mx-auto text-base-content/30 mb-4" />
                <p className="text-base-content/70 mb-4">No recent reviews</p>
                <button className="btn btn-primary btn-sm">
                  Write Your First Review
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {recentReviews.map((review) => (
                  <div key={review.id} className="border-l-4 border-primary pl-4 py-2">
                    <p className="font-semibold">{review.place_name}</p>
                    <p className="text-sm text-base-content/70">
                      {formatDate(review.created_at)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>
          
          {/* Account Info */}
          <Card>
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <User className="text-secondary" />
              Account Information
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-base-content/70">Name</label>
                <p className="font-semibold">{user.name}</p>
              </div>
              
              <div className="divider my-2"></div>
              
              <div>
                <label className="text-sm text-base-content/70">Phone Number</label>
                <p className="font-semibold">{user.phone_number}</p>
              </div>
              
              <div className="divider my-2"></div>
              
              <div>
                <label className="text-sm text-base-content/70 flex items-center gap-2">
                  <Calendar size={16} />
                  Member Since
                </label>
                <p className="font-semibold">
                  {formatDate(userStats.memberSince)}
                </p>
              </div>
            </div>
          </Card>
        </div>
        
        {/* Bookmarked Places */}
        {bookmarks.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Bookmark className="text-primary" />
              Your Bookmarks ({bookmarks.length})
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {bookmarks.slice(0, 6).map((bookmark) => (
                <PlaceCard key={bookmark.id} place={bookmark.place} />
              ))}
            </div>
            
            {bookmarks.length > 6 && (
              <div className="text-center mt-6">
                <button
                  onClick={() => window.location.href = '/bookmarks'}
                  className="btn btn-outline"
                >
                  View All Bookmarks
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;