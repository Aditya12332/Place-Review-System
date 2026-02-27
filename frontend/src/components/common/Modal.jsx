import React, { useEffect } from 'react';
import { X } from 'lucide-react';

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showClose = true,
}) => {
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
    xl: 'max-w-6xl',
  };
  
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);
  
  if (!isOpen) return null;
  
  return (
    <div className="modal modal-open">
      <div className={`modal-box ${sizes[size]} relative`}>
        {showClose && (
          <button
            onClick={onClose}
            className="btn btn-sm btn-circle btn-ghost absolute right-4 top-4"
          >
            <X size={20} />
          </button>
        )}
        
        {title && (
          <h3 className="font-bold text-2xl mb-4">{title}</h3>
        )}
        
        <div className="py-4">
          {children}
        </div>
      </div>
      
      <div className="modal-backdrop" onClick={onClose} />
    </div>
  );
};

export default Modal;