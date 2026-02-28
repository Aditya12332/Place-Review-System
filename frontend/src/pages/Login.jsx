import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Phone, Lock, MapPin } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';
import { validatePhoneNumber } from '../utils/validators';

const Login = () => {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [formData, setFormData] = useState({
    phone_number: '',
    password: ''
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
    
    if (!formData.phone_number) {
      newErrors.phone_number = 'Phone number is required';
    } else if (!validatePhoneNumber(formData.phone_number)) {
      newErrors.phone_number = 'Invalid phone number format';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    try {
      await login(formData);
      toast.success('Login successful!');
      navigate('/');
    } catch (err) {
      // Error is handled by store
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/20 via-base-100 to-secondary/20 px-4 py-12">
      <div className="max-w-md w-full">
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <MapPin className="text-primary" size={40} />
            <h1 className="text-4xl font-bold gradient-text">PlaceReviews</h1>
          </div>
          <p className="text-base-content/70">Discover places with AI-powered insights</p>
        </div>
        
        {/* Login Card */}
        <div className="card bg-base-100 shadow-2xl border border-base-content/10">
          <div className="card-body p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Welcome Back</h2>
            
            {error && (
              <div className="alert alert-error mb-4">
                <span>{error}</span>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
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
                required
              />
              
              {/* Password */}
              <Input
                label="Password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                icon={Lock}
                error={errors.password}
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
                Login
              </Button>
            </form>
            
            {/* Divider */}
            <div className="divider">OR</div>
            
            {/* Register Link */}
            <div className="text-center">
              <p className="text-base-content/70">
                Don't have an account?{' '}
                <Link to="/register" className="link link-primary font-semibold">
                  Sign Up
                </Link>
              </p>
            </div>
          </div>
        </div>
        
        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-info/10 rounded-lg border border-info/20">
          <p className="text-sm text-center text-base-content/70">
            <strong>Demo Account:</strong> Use any phone from test data with password: <code className="bg-base-200 px-2 py-1 rounded">password123</code>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;