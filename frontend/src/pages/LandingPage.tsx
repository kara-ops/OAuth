import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/Button';
import { ShieldCheck, Zap, Lock } from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center">
      <div className="mb-8 p-4 rounded-full border inline-block">
        <ShieldCheck size={48} className="text-primary" />
      </div>
      
      <h1 className="title text-4xl mb-4">
        Simple Authentication
      </h1>
      
      <p className="subtitle mb-8 max-w-2xl text-lg">
        A seamless and secure authentication flow with Google OAuth, local credentials, 
        and robust session management. Built for modern applications.
      </p>
      
      <div className="flex gap-4 mb-16">
        <Link to="/signup">
          <Button variant="primary" className="text-lg px-8 py-3">Get Started</Button>
        </Link>
        <Link to="/login">
          <Button variant="outline" className="text-lg px-8 py-3">Sign In</Button>
        </Link>
      </div>

      <div className="flex gap-8 max-w-4xl w-full justify-center text-left mt-8">
        <div className="card flex-1">
          <Zap className="mb-4" size={24} />
          <h3 className="text-xl font-bold mb-2">Lightning Fast</h3>
          <p className="subtitle">Optimized JWT access tokens with seamless background rotation.</p>
        </div>
        <div className="card flex-1">
          <Lock className="mb-4" size={24} />
          <h3 className="text-xl font-bold mb-2">Bank-grade Security</h3>
          <p className="subtitle">Redis-backed blacklist and secure HTTP-only cookies for maximum safety.</p>
        </div>
      </div>
    </div>
  );
};
