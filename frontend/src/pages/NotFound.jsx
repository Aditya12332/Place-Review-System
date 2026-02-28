import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Search } from 'lucide-react';
import Button from '../components/common/Button';

const NotFound = () => {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200 px-4">
      <div className="text-center max-w-md">
        <h1 className="text-9xl font-bold text-primary mb-4">404</h1>
        <h2 className="text-3xl font-bold mb-4">Page Not Found</h2>
        <p className="text-base-content/70 mb-8">
          Oops! The page you're looking for doesn't exist. 
          It might have been moved or deleted.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            variant="primary"
            onClick={() => navigate('/')}
            className="gap-2"
          >
            <Home size={20} />
            Go Home
          </Button>
          <Button
            variant="outline"
            onClick={() => navigate('/search')}
            className="gap-2"
          >
            <Search size={20} />
            Search Places
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;