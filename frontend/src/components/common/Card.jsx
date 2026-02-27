import React from 'react';

const Card = ({
  children,
  className = '',
  hover = false,
  bordered = true,
  padding = 'normal',
  ...props
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    normal: 'p-6',
    lg: 'p-8',
  };
  
  return (
    <div
      className={`
        card bg-base-100 shadow-lg
        ${bordered ? 'border border-base-content/10' : ''}
        ${hover ? 'card-hover' : ''}
        ${paddingClasses[padding]}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;