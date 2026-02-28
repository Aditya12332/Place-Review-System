import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Phone, Lock, User as UserIcon, MapPin } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';
import { validatePhoneNumber, validatePassword } from '../utils/validators';

const Register = () => {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    clearError();
  };
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }
    
    if (!formData.phone_number) {
      newErrors.phone_number = 'Phone number is required';
    } else if (!validatePhoneNumber(formData.phone_number)) {
      newErrors.phone_number = 'Invalid phone number format (e.g., +1234567890)';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!validatePassword(formData.password)) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    try {
      await register({
        name: formData.name.trim(),
        phone_number: formData.phone_number,
        password: formData.password
      });
      toast.success('Registration successful!');
      navigate('/');
    } catch (err) {
      // Error is handled by store
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-secondary/20 via-base-100 to-primary/20 px-4 py-12">
      <div className="max-w-md w-full">
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <MapPin className="text-primary" size={40} />
            <h1 className="text-4xl font-bold gradient-text">PlaceReviews</h1>
          </div>
          <p className="text-base-content/70">Join our community of reviewers</p>
        </div>
        
        {/* Register Card */}
        <div className="card bg-base-100 shadow-2xl border border-base-content/10">
          <div className="card-body p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Create Account</h2>
            
            {error && (
              <div className="alert alert-error mb-4">
                <span>{error}</span>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name */}
              <Input
                label="Full Name"
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="John Doe"
                icon={UserIcon}
                error={errors.name}
                required
              />
              
              {/* Phone Number */}
              <Input
                label="Phone Number"
                type="tel"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleChange}
                placeholder="+1234567890"
                icon={Phone}
                error={errors.phone_number}
                helperText="Include country code (e.g., +1 for US)"
                required
              />
              
              {/* Password */}
              <Input
                label="Password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Minimum 6 characters"
                icon={Lock}
                error={errors.password}
                required
              />
              
              {/* Confirm Password */}
              <Input
                label="Confirm Password"
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Re-enter your password"
                icon={Lock}
                error={errors.confirmPassword}
                required
              />
              
              {/* Submit Button */}
              <Button
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                isLoading={isLoading}
                className="mt-6"
              >
                Create Account
              </Button>
            </form>
            
            {/* Divider */}
            <div className="divider">OR</div>
            
            {/* Login Link */}
            <div className="text-center">
              <p className="text-base-content/70">
                Already have an account?{' '}
                <Link to="/login" className="link link-primary font-semibold">
                  Login
                </Link>
              </p>
            </div>
          </div>
        </div>
        
        {/* Terms */}
        <p className="text-xs text-center text-base-content/60 mt-6">
          By creating an account, you agree to our{' '}
          <Link to="/terms" className="link">Terms of Service</Link> and{' '}
          <Link to="/privacy" className="link">Privacy Policy</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;