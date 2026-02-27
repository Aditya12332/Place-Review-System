import React from 'react';
import { Star, MessageSquare, Eye, Bookmark } from 'lucide-react';

const PlaceStats = ({ place }) => {
  const stats = [
    {
      icon: Star,
      label: 'Average Rating',
      value: place.average_rating.toFixed(1),
      color: 'text-warning'
    },
    {
      icon: MessageSquare,
      label: 'Total Reviews',
      value: place.total_reviews,
      color: 'text-primary'
    },
    {
      icon: Eye,
      label: 'Views',
      value: place.view_count,
      color: 'text-info'
    },
    {
      icon: Bookmark,
      label: 'Bookmarks',
      value: place.bookmark_count,
      color: 'text-secondary'
    }
  ];
  
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="stats shadow border border-base-content/10"
        >
          <div className="stat p-4">
            <div className={`stat-figure ${stat.color}`}>
              <stat.icon size={32} />
            </div>
            <div className="stat-title text-xs">{stat.label}</div>
            <div className="stat-value text-2xl">{stat.value}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PlaceStats;