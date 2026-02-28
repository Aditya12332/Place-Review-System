import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, TrendingUp, Sparkles, Star, MapPin, Users } from 'lucide-react';
import SearchBar from '../components/search/SearchBar';
import PlaceCard from '../components/place/PlaceCard';
import { usePlaceStore } from '../store/placeStore';
import { PlaceCardSkeleton } from '../components/common/Loading';
import Button from '../components/common/Button';

const Home = () => {
  const navigate = useNavigate();
  const { trendingPlaces, getTrendingPlaces, isLoading } = usePlaceStore();
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    getTrendingPlaces();
    loadStats();
  }, []);
  
  const loadStats = async () => {
    try {
      const { placeService } = await import('../services/placeService');
      const data = await placeService.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats', error);
    }
  };
  
  const handleSearch = (query) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };
  
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary/20 via-base-100 to-secondary/20 py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-2 mb-4">
              <MapPin className="text-primary" size={48} />
              <h1 className="text-5xl md:text-6xl font-bold gradient-text">
                PlaceReviews AI
              </h1>
            </div>
            <p className="text-xl text-base-content/70 mb-2">
              Discover Amazing Places with AI-Powered Insights
            </p>
            <p className="text-base-content/60 flex items-center justify-center gap-2">
              <Sparkles size={16} className="text-primary" />
              Powered by RAG & Groq AI for Intelligent Recommendations
            </p>
          </div>
          
          {/* Search Bar */}
          <div className="max-w-3xl mx-auto mb-8">
            <SearchBar onSearch={handleSearch} showSuggestions={true} />
          </div>
          
          {/* Quick Actions */}
          <div className="flex flex-wrap justify-center gap-4">
            <Button
              variant="primary"
              onClick={() => navigate('/search')}
              className="gap-2"
            >
              <Search size={20} />
              Explore Places
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate('/trending')}
              className="gap-2"
            >
              <TrendingUp size={20} />
              Trending Now
            </Button>
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
              className="gap-2"
            >
              <Sparkles size={20} />
              AI Recommendations
            </Button>
          </div>
        </div>
      </section>
      
      {/* Stats Section */}
      {stats && (
        <section className="py-12 px-4 bg-base-200">
          <div className="container mx-auto max-w-6xl">
            <div className="stats stats-vertical lg:stats-horizontal shadow w-full">
              <div className="stat">
                <div className="stat-figure text-primary">
                  <MapPin size={32} />
                </div>
                <div className="stat-title">Total Places</div>
                <div className="stat-value text-primary">{stats.total_places.toLocaleString()}</div>
              </div>
              
              <div className="stat">
                <div className="stat-figure text-secondary">
                  <Star size={32} />
                </div>
                <div className="stat-title">Total Reviews</div>
                <div className="stat-value text-secondary">{stats.total_reviews.toLocaleString()}</div>
              </div>
              
              <div className="stat">
                <div className="stat-figure text-accent">
                  <Users size={32} />
                </div>
                <div className="stat-title">Active Users</div>
                <div className="stat-value text-accent">{stats.total_users.toLocaleString()}</div>
              </div>
            </div>
          </div>
        </section>
      )}
      
      {/* Features Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">Why Choose PlaceReviews AI?</h2>
            <p className="text-base-content/70 text-lg">
              Experience the future of place discovery with cutting-edge AI technology
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card bg-base-100 shadow-xl border border-primary/20 hover:shadow-2xl transition-shadow">
              <div className="card-body items-center text-center">
                <div className="bg-primary/20 rounded-full p-4 mb-4">
                  <Sparkles className="text-primary" size={32} />
                </div>
                <h3 className="card-title">AI-Powered Summaries</h3>
                <p className="text-base-content/70">
                  Get intelligent summaries of thousands of reviews using advanced RAG technology
                </p>
              </div>
            </div>
            
            {/* Feature 2 */}
            <div className="card bg-base-100 shadow-xl border border-secondary/20 hover:shadow-2xl transition-shadow">
              <div className="card-body items-center text-center">
                <div className="bg-secondary/20 rounded-full p-4 mb-4">
                  <TrendingUp className="text-secondary" size={32} />
                </div>
                <h3 className="card-title">Sentiment Analysis</h3>
                <p className="text-base-content/70">
                  Understand overall sentiment with detailed positive/negative/neutral breakdowns
                </p>
              </div>
            </div>
            
            {/* Feature 3 */}
            <div className="card bg-base-100 shadow-xl border border-accent/20 hover:shadow-2xl transition-shadow">
              <div className="card-body items-center text-center">
                <div className="bg-accent/20 rounded-full p-4 mb-4">
                  <Search className="text-accent" size={32} />
                </div>
                <h3 className="card-title">Smart Search</h3>
                <p className="text-base-content/70">
                  Find exactly what you're looking for with AI-enhanced search suggestions
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Trending Places Section */}
      <section className="py-16 px-4 bg-base-200">
        <div className="container mx-auto max-w-6xl">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold flex items-center gap-2">
                <TrendingUp className="text-primary" />
                Trending Places
              </h2>
              <p className="text-base-content/70 mt-2">
                Discover what's popular right now
              </p>
            </div>
            <Button
              variant="outline"
              onClick={() => navigate('/search')}
            >
              View All
            </Button>
          </div>
          
          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <PlaceCardSkeleton key={i} />
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {trendingPlaces.slice(0, 6).map((place) => (
                <PlaceCard key={place.id} place={place} />
              ))}
            </div>
          )}
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-br from-primary to-secondary text-white">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Discover Your Next Favorite Place?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of users making smarter decisions with AI-powered insights
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button
              variant="accent"
              size="lg"
              onClick={() => navigate('/register')}
              className="gap-2"
            >
              Get Started Free
            </Button>
            <Button
              variant="ghost"
              size="lg"
              onClick={() => navigate('/search')}
              className="gap-2 text-white border-white hover:bg-white/20"
            >
              Explore Places
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;