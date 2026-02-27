import React from 'react';
import { Loader2 } from 'lucide-react';

const Loading = ({ 
  size = 'md', 
  fullScreen = false,
  text = 'Loading...'
}) => {
  const sizes = {
    sm: 24,
    md: 40,
    lg: 56,
  };
  
  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <Loader2 className="animate-spin text-primary" size={sizes[size]} />
      {text && <p className="text-base-content/70 font-medium">{text}</p>}
    </div>
  );
  
  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-base-100 flex items-center justify-center z-50">
        {content}
      </div>
    );
  }
  
  return (
    <div className="flex items-center justify-center py-12">
      {content}
    </div>
  );
};

export default Loading;

// Skeleton loading component
export const Skeleton = ({ className = '', variant = 'text' }) => {
  const variants = {
    text: 'h-4 w-full',
    title: 'h-8 w-3/4',
    avatar: 'h-12 w-12 rounded-full',
    card: 'h-64 w-full',
  };
  
  return (
    <div className={`skeleton ${variants[variant]} ${className}`} />
  );
};

// Card skeleton for place cards
export const PlaceCardSkeleton = () => {
  return (
    <div className="card bg-base-100 shadow-lg border border-base-content/10 p-6">
      <Skeleton variant="card" className="mb-4" />
      <Skeleton variant="title" className="mb-2" />
      <Skeleton variant="text" className="mb-2" />
      <Skeleton variant="text" className="w-1/2" />
    </div>
  );
};