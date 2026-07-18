import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/Card';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import apiClient from '../api/apiClient';

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<{type: 'idle' | 'success' | 'error', message: string}>({
    type: 'idle', message: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: 'idle', message: '' });
    
    try {
      await apiClient.post('/auth/forgot-password', { email });
      setStatus({ 
        type: 'success', 
        message: 'If an account exists with that email, a password reset link has been sent.' 
      });
    } catch (err: any) {
      setStatus({ 
        type: 'error', 
        message: err.response?.data?.detail || 'Failed to request password reset. Please try again.' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center flex-1 mt-12">
      <Card className="w-full max-w-md">
        <div className="text-center mb-6">
          <h2 className="title text-3xl">Reset Password</h2>
          <p className="subtitle">Enter your email to receive a reset link</p>
        </div>
        
        {status.type === 'success' ? (
          <div className="text-center">
            <div className="border success-text p-4 rounded-lg mb-6">
              {status.message}
            </div>
            <Link to="/login">
              <Button variant="outline" className="w-full">Return to Login</Button>
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <Input 
              label="Email Address" 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
            />
            
            {status.type === 'error' && (
              <p className="error-text mb-4">{status.message}</p>
            )}
            
            <Button type="submit" className="w-full mt-2 mb-4" isLoading={loading}>
              Send Reset Link
            </Button>
            
            <div className="text-center mt-4">
              <Link to="/login" className="text-sm text-primary hover:underline">
                Back to sign in
              </Link>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
};
