import React from 'react';
import { MapPin, Github, Twitter, Linkedin, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-base-200 border-t border-base-content/10 mt-auto">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <MapPin className="text-primary" size={32} />
              <span className="text-2xl font-bold gradient-text">PlaceReviews AI</span>
            </Link>
            <p className="text-base-content/70 mb-4">
              Discover and review amazing places with the power of AI. 
              Get intelligent insights, personalized recommendations, and make informed decisions.
            </p>
            <div className="flex gap-3">
              <a href="#" className="btn btn-circle btn-ghost btn-sm">
                <Github size={20} />
              </a>
              <a href="#" className="btn btn-circle btn-ghost btn-sm">
                <Twitter size={20} />
              </a>
              <a href="#" className="btn btn-circle btn-ghost btn-sm">
                <Linkedin size={20} />
              </a>
            </div>
          </div>
          
          {/* Quick Links */}
          <div>
            <h3 className="font-bold text-lg mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/search" className="link link-hover">Search Places</Link>
              </li>
              <li>
                <Link to="/trending" className="link link-hover">Trending</Link>
              </li>
              <li>
                <Link to="/categories" className="link link-hover">Categories</Link>
              </li>
              <li>
                <Link to="/about" className="link link-hover">About Us</Link>
              </li>
            </ul>
          </div>
          
          {/* Support */}
          <div>
            <h3 className="font-bold text-lg mb-4">Support</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/help" className="link link-hover">Help Center</Link>
              </li>
              <li>
                <Link to="/contact" className="link link-hover">Contact Us</Link>
              </li>
              <li>
                <Link to="/privacy" className="link link-hover">Privacy Policy</Link>
              </li>
              <li>
                <Link to="/terms" className="link link-hover">Terms of Service</Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="divider"></div>
        
        {/* Bottom */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-base-content/70 text-sm text-center md:text-left">
            © {currentYear} PlaceReviews AI. All rights reserved.
          </p>
          <p className="text-base-content/70 text-sm flex items-center gap-1">
            Made with <Heart size={16} className="text-error" fill="currentColor" /> using RAG & Groq AI
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;