import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

export const OAuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const token = searchParams.get('access_token');
    
    if (token) {
      setTimeout(async () => {
        try {
          await login(token);
          navigate('/dashboard', { replace: true });
        } catch (error) {
          console.error("Failed to login with OAuth token", error);
          navigate('/login', { replace: true });
        }
      }, 100);
    } else {
      navigate('/login', { replace: true });
    }
  }, [searchParams, navigate, login]);

  return (
    <div className="flex flex-col items-center justify-center flex-1 h-screen">
      <Loader2 className="animate-spin mb-4" size={48} color="#2563eb" />
      <h2 className="text-xl font-medium">Authenticating...</h2>
      <p className="subtitle mt-2">Please wait while we log you in.</p>
    </div>
  );
};
