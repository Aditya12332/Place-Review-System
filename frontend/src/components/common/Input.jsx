import React from 'react';

const Input = ({
  label,
  type = 'text',
  name,
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  helperText,
  required = false,
  disabled = false,
  className = '',
  icon: Icon,
  ...props
}) => {
  return (
    <div className={`form-control w-full ${className}`}>
      {label && (
        <label className="label">
          <span className="label-text font-medium">
            {label}
            {required && <span className="text-error ml-1">*</span>}
          </span>
        </label>
      )}
      
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-base-content/50">
            <Icon size={20} />
          </div>
        )}
        
        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          className={`
            input input-bordered w-full
            ${Icon ? 'pl-10' : ''}
            ${error ? 'input-error' : ''}
            ${disabled ? 'input-disabled' : ''}
          `}
          {...props}
        />
      </div>
      
      {error && (
        <label className="label">
          <span className="label-text-alt text-error">{error}</span>
        </label>
      )}
      
      {helperText && !error && (
        <label className="label">
          <span className="label-text-alt text-base-content/60">{helperText}</span>
        </label>
      )}
    </div>
  );
};

export default Input;