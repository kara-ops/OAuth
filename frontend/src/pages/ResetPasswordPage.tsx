import React from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { AlertTriangle } from 'lucide-react';

export const ResetPasswordPage: React.FC = () => {
  return (
    <div className="flex items-center justify-center flex-1 mt-12">
      <Card className="w-full max-w-md">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div style={{ padding: '0.75rem', borderRadius: '9999px', backgroundColor: '#fef3c7' }}>
              <AlertTriangle size={32} style={{ color: '#d97706' }} />
            </div>
          </div>
          <h2 className="title text-3xl" style={{ marginBottom: '0.5rem' }}>Service Unavailable</h2>
          <p className="subtitle" style={{ marginBottom: '1.5rem' }}>
            This service is currently down. Please try again later.
          </p>
          <Link to="/login">
            <Button variant="outline" className="w-full">Back to Sign In</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
};
