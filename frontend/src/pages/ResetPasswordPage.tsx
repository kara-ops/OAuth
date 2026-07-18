import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Card } from '../components/Card';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import apiClient from '../api/apiClient';

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [status, setStatus] = useState<{type: 'idle' | 'success' | 'error', message: string}>({
    type: 'idle', message: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: 'idle', message: '' });
    
    if (!token) {
      setStatus({ type: 'error', message: 'Missing reset token in URL.' });
      setLoading(false);
      return;
    }

    try {
      await apiClient.patch(`/auth/set-password?token=${token}`, { 
        code, 
        new_password: newPassword 
      });
      
      setStatus({ 
        type: 'success', 
        message: 'Your password has been successfully reset.' 
      });
      
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      setStatus({ 
        type: 'error', 
        message: err.response?.data?.detail || 'Failed to reset password. The code might be invalid or expired.' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center flex-1 mt-12">
      <Card className="w-full max-w-md">
        <div className="text-center mb-6">
          <h2 className="title text-3xl">Set New Password</h2>
          <p className="subtitle">Enter your reset code and new password</p>
        </div>
        
        {status.type === 'success' ? (
          <div className="text-center">
            <div className="border success-text p-4 rounded-lg mb-6">
              {status.message}
            </div>
            <p className="subtitle mb-4">Redirecting to login...</p>
            <Link to="/login">
              <Button variant="primary" className="w-full">Go to Login</Button>
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <Input 
              label="Reset Code" 
              type="text" 
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              placeholder="Enter the code sent to your email"
            />
            
            <Input 
              label="New Password" 
              type="password" 
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              placeholder="••••••••"
              minLength={8}
            />
            
            {status.type === 'error' && (
              <p className="error-text mb-4">{status.message}</p>
            )}
            
            <Button type="submit" className="w-full mt-2 mb-4" isLoading={loading}>
              Reset Password
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
};
