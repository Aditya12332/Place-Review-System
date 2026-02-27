import React, { useState, useEffect } from 'react';
import { Search, X, Sparkles } from 'lucide-react';
import { useDebounce } from '../../hooks/useDebounce';
import { aiService } from '../../services/aiService';

const SearchBar = ({ onSearch, placeholder = 'Search for places...', showSuggestions = true }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestionsList, setShowSuggestionsList] = useState(false);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  
  const debouncedQuery = useDebounce(query, 300);
  
  useEffect(() => {
    if (debouncedQuery && debouncedQuery.length >= 2 && showSuggestions) {
      loadSuggestions(debouncedQuery);
    } else {
      setSuggestions([]);
    }
  }, [debouncedQuery]);
  
  const loadSuggestions = async (searchQuery) => {
    setIsLoadingSuggestions(true);
    try {
      const data = await aiService.getSearchSuggestions(searchQuery);
      setSuggestions(data.suggestions || []);
      setShowSuggestionsList(true);
    } catch (error) {
      console.error('Failed to load suggestions', error);
      setSuggestions([]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
      setShowSuggestionsList(false);
    }
  };
  
  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    onSearch(suggestion);
    setShowSuggestionsList(false);
  };
  
  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestionsList(false);
  };
  
  return (
    <div className="relative w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-base-content/50" size={20} />
          
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => suggestions.length > 0 && setShowSuggestionsList(true)}
            placeholder={placeholder}
            className="input input-bordered w-full pl-12 pr-12 h-14 text-lg"
          />
          
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-4 top-1/2 -translate-y-1/2 btn btn-ghost btn-circle btn-sm"
            >
              <X size={20} />
            </button>
          )}
        </div>
        
        <button type="submit" className="sr-only">Search</button>
      </form>
      
      {/* AI Suggestions Dropdown */}
      {showSuggestionsList && suggestions.length > 0 && (
        <>
          <div 
            className="fixed inset-0 z-10"
            onClick={() => setShowSuggestionsList(false)}
          />
          <div className="absolute top-full left-0 right-0 mt-2 bg-base-100 rounded-lg shadow-xl border border-base-content/10 z-20 max-h-80 overflow-y-auto">
            <div className="p-3 border-b border-base-content/10 flex items-center gap-2">
              <Sparkles size={16} className="text-primary" />
              <span className="text-sm font-semibold text-primary">AI-Powered Suggestions</span>
            </div>
            
            {isLoadingSuggestions ? (
              <div className="p-4 text-center">
                <span className="loading loading-spinner loading-sm"></span>
              </div>
            ) : (
              <ul className="py-2">
                {suggestions.map((suggestion, index) => (
                  <li key={index}>
                    <button
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="w-full px-4 py-3 text-left hover:bg-base-200 transition-colors flex items-center gap-3"
                    >
                      <Search size={16} className="text-base-content/50" />
                      <span>{suggestion}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default SearchBar;