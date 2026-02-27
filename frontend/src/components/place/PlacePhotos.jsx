import React, { useState } from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import Modal from '../common/Modal';

const PlacePhotos = ({ photos = [] }) => {
  const [selectedIndex, setSelectedIndex] = useState(null);
  
  if (photos.length === 0) {
    return (
      <div className="bg-base-200 rounded-lg p-8 text-center">
        <p className="text-base-content/70">No photos available</p>
      </div>
    );
  }
  
  const openLightbox = (index) => {
    setSelectedIndex(index);
  };
  
  const closeLightbox = () => {
    setSelectedIndex(null);
  };
  
  const goToPrevious = () => {
    setSelectedIndex((prev) => (prev > 0 ? prev - 1 : photos.length - 1));
  };
  
  const goToNext = () => {
    setSelectedIndex((prev) => (prev < photos.length - 1 ? prev + 1 : 0));
  };
  
  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {photos.map((photo, index) => (
          <button
            key={photo.id}
            onClick={() => openLightbox(index)}
            className="relative aspect-square rounded-lg overflow-hidden group cursor-pointer border border-base-content/10"
          >
            <img
              src={photo.image_url}
              alt={photo.caption || 'Place photo'}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
            />
            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
              <span className="text-white font-semibold">View</span>
            </div>
          </button>
        ))}
      </div>
      
      {/* Lightbox Modal */}
      {selectedIndex !== null && (
        <div className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center">
          {/* Close button */}
          <button
            onClick={closeLightbox}
            className="absolute top-4 right-4 btn btn-circle btn-ghost text-white hover:bg-white/20"
          >
            <X size={24} />
          </button>
          
          {/* Previous button */}
          <button
            onClick={goToPrevious}
            className="absolute left-4 btn btn-circle btn-ghost text-white hover:bg-white/20"
          >
            <ChevronLeft size={24} />
          </button>
          
          {/* Image */}
          <div className="max-w-5xl max-h-[80vh] p-4">
            <img
              src={photos[selectedIndex].image_url}
              alt={photos[selectedIndex].caption || 'Place photo'}
              className="max-w-full max-h-full object-contain rounded-lg"
            />
            {photos[selectedIndex].caption && (
              <p className="text-white text-center mt-4">
                {photos[selectedIndex].caption}
              </p>
            )}
            <p className="text-white/70 text-center text-sm mt-2">
              {selectedIndex + 1} / {photos.length}
            </p>
          </div>
          
          {/* Next button */}
          <button
            onClick={goToNext}
            className="absolute right-4 btn btn-circle btn-ghost text-white hover:bg-white/20"
          >
            <ChevronRight size={24} />
          </button>
        </div>
      )}
    </>
  );
};

export default PlacePhotos;