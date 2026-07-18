import React, { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/apiClient';
import { Loader2, Monitor, Smartphone } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await apiClient.get('/auth/get-session');
        setSessions(Array.isArray(res.data) ? res.data : [res.data]);
      } catch (error) {
        console.error('Failed to fetch sessions', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSessions();
  }, []);

  return (
    <div className="mt-8 w-full max-w-4xl mx-auto">
      <h1 className="title text-3xl mb-2">Dashboard</h1>
      <p className="subtitle mb-8">Manage your account and active sessions</p>

      <div className="flex gap-8 flex-col md:flex-row">
        <Card className="flex-1">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            Profile Information
          </h2>
          
          <div className="space-y-4">
            <div>
              <p className="subtitle">Email Address</p>
              <p className="font-medium">{user?.email}</p>
            </div>
            <div>
              <p className="subtitle">Account Status</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`w-2 h-2 rounded-full ${user?.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span>{user?.is_active ? 'Active' : 'Inactive'}</span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="flex-[2]">
          <h2 className="text-xl font-bold mb-6">Active Sessions</h2>
          
          {loading ? (
            <div className="flex justify-center p-8">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : sessions.length > 0 ? (
            <div className="space-y-4">
              {sessions.map((session, index) => (
                <div key={index} className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-4">
                    <div className="p-2 border rounded-full bg-gray-50">
                      {session.device_metadata?.toLowerCase().includes('mobile') ? <Smartphone size={20} /> : <Monitor size={20} />}
                    </div>
                    <div>
                      <p className="font-medium">
                        {session.ip_address || 'Unknown IP'}
                      </p>
                      <p className="subtitle">
                        {session.user_agent || 'Unknown Device'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-medium px-2 py-1 rounded-full border success-text inline-block mt-0">
                      Active
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="subtitle">No active sessions found.</p>
          )}
        </Card>
      </div>
    </div>
  );
};
