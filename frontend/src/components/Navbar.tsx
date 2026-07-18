import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './Button';
import { ShieldCheck, LogOut, User } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <nav className="nav-header">
      <Link to="/" className="nav-brand">
        <ShieldCheck className="text-primary" size={24} />
        <span>SecureAuth</span>
      </Link>
      
      <div className="flex items-center gap-4">
        {user ? (
          <>
            <Link to="/dashboard">
              <Button variant="outline" className="gap-2">
                <User size={18} />
                Dashboard
              </Button>
            </Link>
            <Button variant="primary" onClick={handleLogout} className="gap-2">
              <LogOut size={18} />
              Logout
            </Button>
          </>
        ) : (
          <>
            <Link to="/login">
              <Button variant="outline">Sign In</Button>
            </Link>
            <Link to="/signup">
              <Button variant="primary">Get Started</Button>
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};
