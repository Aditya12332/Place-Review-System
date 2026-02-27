import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Search, 
  MapPin, 
  Bookmark, 
  User, 
  LogOut, 
  Moon, 
  Sun,
  Menu,
  X,
  Sparkles
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { useUIStore } from '../../store/uiStore';

const Navbar = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme, isMobileMenuOpen, toggleMobileMenu } = useUIStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <nav className="navbar bg-base-100 shadow-lg sticky top-0 z-50 border-b border-base-content/10">
      <div className="container mx-auto">
        {/* Mobile menu button */}
        <div className="navbar-start">
          <button
            onClick={toggleMobileMenu}
            className="btn btn-ghost btn-circle lg:hidden"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          
          <Link to="/" className="btn btn-ghost normal-case text-xl font-bold hidden lg:flex items-center gap-2">
            <MapPin className="text-primary" size={28} />
            <span className="gradient-text">PlaceReviews</span>
            <span className="badge badge-secondary badge-sm">AI</span>
          </Link>
        </div>
        
        {/* Center - Logo for mobile */}
        <div className="navbar-center lg:hidden">
          <Link to="/" className="btn btn-ghost normal-case text-xl font-bold flex items-center gap-2">
            <MapPin className="text-primary" size={24} />
            <span className="gradient-text">PlaceReviews</span>
          </Link>
        </div>
        
        {/* Desktop menu */}
        <div className="navbar-center hidden lg:flex">
          <ul className="menu menu-horizontal px-1 gap-2">
            <li>
              <Link to="/search" className="gap-2">
                <Search size={18} />
                Search
              </Link>
            </li>
            <li>
              <Link to="/trending" className="gap-2">
                <Sparkles size={18} />
                Trending
              </Link>
            </li>
            <li>
              <Link to="/bookmarks" className="gap-2">
                <Bookmark size={18} />
                Bookmarks
              </Link>
            </li>
          </ul>
        </div>
        
        {/* Right side */}
        <div className="navbar-end gap-2">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="btn btn-ghost btn-circle"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
          
          {/* User menu */}
          {user ? (
            <div className="dropdown dropdown-end">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="btn btn-ghost btn-circle avatar placeholder"
              >
                <div className="bg-primary text-primary-content rounded-full w-10">
                  <span className="text-lg font-semibold">
                    {user.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              </button>
              
              {showUserMenu && (
                <ul className="menu dropdown-content mt-3 z-[1] p-2 shadow-lg bg-base-100 rounded-box w-52 border border-base-content/10">
                  <li className="menu-title">
                    <span>{user.name}</span>
                  </li>
                  <li>
                    <Link to="/dashboard" onClick={() => setShowUserMenu(false)}>
                      <User size={18} />
                      Dashboard
                    </Link>
                  </li>
                  <li>
                    <Link to="/bookmarks" onClick={() => setShowUserMenu(false)}>
                      <Bookmark size={18} />
                      My Bookmarks
                    </Link>
                  </li>
                  <div className="divider my-0"></div>
                  <li>
                    <button onClick={handleLogout} className="text-error">
                      <LogOut size={18} />
                      Logout
                    </button>
                  </li>
                </ul>
              )}
            </div>
          ) : (
            <div className="flex gap-2">
              <Link to="/login" className="btn btn-ghost btn-sm">
                Login
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
      
      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="lg:hidden absolute top-full left-0 right-0 bg-base-100 border-b border-base-content/10 shadow-lg">
          <ul className="menu menu-vertical p-4 gap-2">
            <li>
              <Link to="/search" onClick={toggleMobileMenu}>
                <Search size={18} />
                Search Places
              </Link>
            </li>
            <li>
              <Link to="/trending" onClick={toggleMobileMenu}>
                <Sparkles size={18} />
                Trending
              </Link>
            </li>
            <li>
              <Link to="/bookmarks" onClick={toggleMobileMenu}>
                <Bookmark size={18} />
                My Bookmarks
              </Link>
            </li>
            {user && (
              <>
                <div className="divider my-2"></div>
                <li>
                  <Link to="/dashboard" onClick={toggleMobileMenu}>
                    <User size={18} />
                    Dashboard
                  </Link>
                </li>
              </>
            )}
          </ul>
        </div>
      )}
    </nav>
  );
};

export default Navbar;