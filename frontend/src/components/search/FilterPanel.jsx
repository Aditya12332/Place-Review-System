import React, { useState, useEffect } from 'react';
import { Filter, X, Star } from 'lucide-react';
import { usePlaceStore } from '../../store/placeStore';
import Button from '../common/Button';

const FilterPanel = ({ onFilterChange, initialFilters = {} }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState({
    category: initialFilters.category || '',
    min_rating: initialFilters.min_rating || '',
  });
  
  const { categories, getCategories } = usePlaceStore();
  
  useEffect(() => {
    getCategories();
  }, []);
  
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };
  
  const handleApply = () => {
    onFilterChange(filters);
    setIsOpen(false);
  };
  
  const handleClear = () => {
    const clearedFilters = { category: '', min_rating: '' };
    setFilters(clearedFilters);
    onFilterChange(clearedFilters);
  };
  
  const activeFilterCount = Object.values(filters).filter(v => v).length;
  
  return (
    <>
      {/* Filter Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn btn-outline gap-2"
      >
        <Filter size={20} />
        Filters
        {activeFilterCount > 0 && (
          <span className="badge badge-primary badge-sm">{activeFilterCount}</span>
        )}
      </button>
      
      {/* Filter Panel - Desktop Sidebar / Mobile Drawer */}
      {isOpen && (
        <>
          <div 
            className="fixed inset-0 bg-black/50 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          <div className="fixed right-0 top-0 h-full w-full sm:w-96 bg-base-100 z-50 shadow-2xl overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold">Filters</h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="btn btn-ghost btn-circle btn-sm"
                >
                  <X size={20} />
                </button>
              </div>
              
              {/* Category Filter */}
              <div className="mb-6">
                <label className="label">
                  <span className="label-text font-semibold">Category</span>
                </label>
                <select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="select select-bordered w-full"
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.icon} {cat.name}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Rating Filter */}
              <div className="mb-6">
                <label className="label">
                  <span className="label-text font-semibold">Minimum Rating</span>
                </label>
                <div className="grid grid-cols-5 gap-2">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      onClick={() => handleFilterChange('min_rating', rating.toString())}
                      className={`btn ${
                        filters.min_rating === rating.toString()
                          ? 'btn-primary'
                          : 'btn-outline'
                      }`}
                    >
                      {rating}
                      <Star size={14} fill={filters.min_rating === rating.toString() ? 'currentColor' : 'none'} />
                    </button>
                  ))}
                </div>
                {filters.min_rating && (
                  <p className="text-sm text-base-content/70 mt-2">
                    Showing places rated {filters.min_rating}+ stars
                  </p>
                )}
              </div>
              
              {/* Action Buttons */}
              <div className="flex gap-3 mt-8">
                <Button
                  variant="outline"
                  onClick={handleClear}
                  fullWidth
                >
                  Clear All
                </Button>
                <Button
                  variant="primary"
                  onClick={handleApply}
                  fullWidth
                >
                  Apply Filters
                </Button>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default FilterPanel;