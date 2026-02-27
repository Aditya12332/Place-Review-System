import React from 'react';
import { Search, Inbox, BookmarkX } from 'lucide-react';

const EmptyState = ({ 
  icon: Icon = Inbox,
  title,
  description,
  action,
  actionLabel
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="bg-base-200 rounded-full p-6 mb-6">
        <Icon size={48} className="text-base-content/30" />
      </div>
      
      <h3 className="text-2xl font-bold text-center mb-2">
        {title}
      </h3>
      
      {description && (
        <p className="text-base-content/70 text-center max-w-md mb-6">
          {description}
        </p>
      )}
      
      {action && actionLabel && (
        <button onClick={action} className="btn btn-primary">
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;