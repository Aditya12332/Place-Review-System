import React, { useState, useEffect } from 'react';
import { Sparkles, Heart } from 'lucide-react';
import { aiService } from '../../services/aiService';
import Loading from '../common/Loading';
import EmptyState from '../common/EmptyState';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [basedOnReviews, setBasedOnReviews] = useState(0);
  
  useEffect(() => {
    loadRecommendations();
  }, []);
  
  const loadRecommendations = async () => {
    setIsLoading(true);
    try {
      const data = await aiService.getRecommendations();
      setRecommendations(data.recommendations || []);
      setBasedOnReviews(data.based_on_reviews || 0);
    } catch (error) {
      console.error('Failed to load recommendations', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return <Loading text="Generating personalized recommendations..." />;
  }
  
  if (recommendations.length === 0) {
    return (
      <EmptyState
        icon={Heart}
        title="No recommendations yet"
        description="Start reviewing places to get personalized AI recommendations!"
      />
    );
  }
  
  return (
    <div className="card bg-gradient-to-br from-secondary/10 to-accent/10 border border-secondary/20 shadow-xl">
      <div className="card-body">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="text-secondary" size={24} />
          <h3 className="text-2xl font-bold">Personalized for You</h3>
        </div>
        
        <p className="text-base-content/70 mb-6">
          Based on your {basedOnReviews} reviews, here's what we think you'll love:
        </p>
        
        <div className="grid md:grid-cols-2 gap-4">
          {recommendations.map((rec, index) => (
            <div
              key={index}
              className="bg-base-100 rounded-lg p-6 border border-base-content/10 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start gap-3">
                <div className="bg-secondary/20 rounded-full p-2 flex-shrink-0">
                  <Heart className="text-secondary" size={20} />
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-2">{rec.type}</h4>
                  <p className="text-sm text-base-content/70">{rec.reason}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-xs text-base-content/60 mt-6 text-center">
          Powered by RAG AI • Updates as you review more places
        </div>
      </div>
    </div>
  );
};

export default Recommendations;