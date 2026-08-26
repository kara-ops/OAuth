import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/Button';
import { ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LandingPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center px-4">
      <div className="mb-8 p-5 rounded-2xl bg-primary/10 inline-block">
        <ShieldCheck size={56} className="text-primary" />
      </div>
      
      <h1 className="text-5xl font-bold tracking-tight text-gray-900 mb-6">
        Authenticator
      </h1>
      
      <p className="text-xl text-gray-500 mb-12 max-w-md mx-auto leading-relaxed">
        Secure access to your workspace.
      </p>
      
      <div className="flex flex-col sm:flex-row gap-4 w-full max-w-sm mx-auto">
        {user ? (
          <Link to="/dashboard" className="w-full">
            <Button variant="primary" className="w-full text-lg py-4 rounded-xl shadow-sm hover:shadow-md transition-all">
              Go to Dashboard
            </Button>
          </Link>
        ) : (
          <>
            <Link to="/login" className="w-full sm:w-1/2">
              <Button variant="outline" className="w-full text-lg py-3 rounded-xl border-gray-200 text-gray-700 hover:bg-gray-50">
                Sign In
              </Button>
            </Link>
            <Link to="/signup" className="w-full sm:w-1/2">
              <Button variant="primary" className="w-full text-lg py-3 rounded-xl shadow-sm hover:shadow-md transition-all">
                Create Account
              </Button>
            </Link>
          </>
        )}
      </div>
    </div>
  );
};
