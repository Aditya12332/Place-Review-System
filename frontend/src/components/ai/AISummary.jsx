import React, { useState, useEffect } from 'react';
import { Sparkles, RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { aiService } from '../../services/aiService';
import Button from '../common/Button';
import Loading from '../common/Loading';
import toast from 'react-hot-toast';
import { getSentimentEmoji } from '../../utils/helpers';

const AISummary = ({ placeId }) => {
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);

  useEffect(() => {
    loadSummary();
  }, [placeId]);
  
  const loadSummary = async () => {
    setIsLoading(true);
    try {
      const data = await aiService.getPlaceSummary(placeId);
      setSummary(data);
    } catch (error) {
      console.error('Failed to load AI summary', error);
      toast.error('Failed to load AI insights');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      const data = await aiService.regenerateSummary(placeId);
      setSummary(data.summary);
      toast.success('Summary regenerated successfully');
    } catch (error) {
      toast.error('Failed to regenerate summary');
    } finally {
      setIsRegenerating(false);
    }
  };
  
  if (isLoading) {
    return <Loading text="Generating AI insights..." />;
  }
  
  if (!summary) {
    return null;
  }
  
  const getSentimentIcon = (label) => {
    if (label === 'positive') return <TrendingUp className="text-success" />;
    if (label === 'negative') return <TrendingDown className="text-error" />;
    return <Minus className="text-base-content/50" />;
  };
  
  return (
    <div className="card bg-gradient-to-br from-primary/10 to-secondary/10 border border-primary/20 shadow-xl">
      <div className="card-body">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="text-primary" size={24} />
            <h3 className="text-2xl font-bold">AI-Powered Insights</h3>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRegenerate}
            isLoading={isRegenerating}
            className="gap-2"
          >
            <RefreshCw size={16} />
            Regenerate
          </Button>
        </div>
        
        {/* Summary */}
        <div className="bg-base-100 rounded-lg p-6 mb-6">
          <p className="text-lg leading-relaxed">{summary.summary}</p>
        </div>
        
        {/* Sentiment Analysis */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Overall Sentiment */}
          <div className="bg-base-100 rounded-lg p-6">
            <h4 className="font-semibold mb-4 flex items-center gap-2">
              {getSentimentIcon(summary.sentiment_label)}
              Overall Sentiment
            </h4>
            
            <div className="flex items-center gap-3 mb-4">
              <span className="text-4xl">
                {getSentimentEmoji(summary.sentiment_label)}
              </span>
              <div>
                <p className="text-2xl font-bold capitalize">
                  {summary.sentiment_label}
                </p>
                <p className="text-sm text-base-content/60">
                  Score: {summary.sentiment_score.toFixed(2)}
                </p>
              </div>
            </div>
            
            {/* Sentiment Breakdown */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-success"></span>
                  Positive
                </span>
                <span className="font-semibold">{summary.positive_percentage.toFixed(0)}%</span>
              </div>
              <progress
                className="progress progress-success w-full"
                value={summary.positive_percentage}
                max="100"
              ></progress>
              
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-base-content/50"></span>
                  Neutral
                </span>
                <span className="font-semibold">{summary.neutral_percentage.toFixed(0)}%</span>
              </div>
              <progress
                className="progress w-full"
                value={summary.neutral_percentage}
                max="100"
              ></progress>
              
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-error"></span>
                  Negative
                </span>
                <span className="font-semibold">{summary.negative_percentage.toFixed(0)}%</span>
              </div>
              <progress
                className="progress progress-error w-full"
                value={summary.negative_percentage}
                max="100"
              ></progress>
            </div>
          </div>
          
          {/* Keywords & Insights */}
          <div className="bg-base-100 rounded-lg p-6">
            {/* Top Keywords */}
            <h4 className="font-semibold mb-3">Top Keywords</h4>
            <div className="flex flex-wrap gap-2 mb-6">
              {summary.top_keywords.map((keyword, index) => (
                <span key={index} className="badge badge-primary badge-lg">
                  {keyword}
                </span>
              ))}
            </div>
            
            {/* Highlights */}
            {summary.highlights.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2 text-success flex items-center gap-2">
                  <TrendingUp size={18} />
                  What People Love
                </h4>
                <ul className="space-y-1">
                  {summary.highlights.map((highlight, index) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <span className="text-success mt-1">✓</span>
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Concerns */}
            {summary.concerns.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-warning flex items-center gap-2">
                  <TrendingDown size={18} />
                  Areas for Improvement
                </h4>
                <ul className="space-y-1">
                  {summary.concerns.map((concern, index) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <span className="text-warning mt-1">!</span>
                      <span>{concern}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
        
        {/* Footer */}
        <div className="text-xs text-base-content/60 mt-4 text-center">
          Generated using RAG-powered AI • Based on {summary.review_count_at_generation} reviews
        </div>
      </div>
    </div>
  );
};

export default AISummary;