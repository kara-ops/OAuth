import React, { useEffect, useState } from 'react';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/apiClient';
import { Loader2, Monitor, Smartphone, KeyRound, User as UserIcon, ChevronDown } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  // Using activeTab to control accordion state (null means all closed)
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'sessions' | null>('profile');
  
  // Sessions state
  const [sessions, setSessions] = useState<any[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);

  // Password reset state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [passStatus, setPassStatus] = useState<{type: 'idle'|'success'|'error', msg: string}>({type: 'idle', msg: ''});
  const [passLoading, setPassLoading] = useState(false);

  // Add password state (for Google users)
  const [addPasswordText, setAddPasswordText] = useState('');
  const [addPassStatus, setAddPassStatus] = useState<{type: 'idle'|'success'|'error', msg: string}>({type: 'idle', msg: ''});
  const [addPassLoading, setAddPassLoading] = useState(false);

  const toggleTab = (tab: 'profile' | 'security' | 'sessions') => {
    setActiveTab(activeTab === tab ? null : tab);
  };

  const handleAddPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddPassLoading(true);
    setAddPassStatus({ type: 'idle', msg: '' });
    try {
      await apiClient.post('/auth/add-password', {
        new_password: addPasswordText
      });
      setAddPassStatus({ type: 'success', msg: 'Password added successfully' });
      setAddPasswordText('');
    } catch (err: any) {
      setAddPassStatus({ 
        type: 'error', 
        msg: err.response?.data?.detail || 'Failed to add password' 
      });
    } finally {
      setAddPassLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'sessions' && sessions.length === 0) {
      const fetchSessions = async () => {
        setLoadingSessions(true);
        try {
          const res = await apiClient.get('/auth/get-session');
          if (res.data && Array.isArray(res.data.last_seen)) {
            const formattedSessions = res.data.last_seen.map((lastSeen: any, i: number) => ({
              last_seen: lastSeen,
              device_type: res.data.device_type?.[i],
              device_name: res.data.device_name?.[i]
            }));
            setSessions(formattedSessions);
          } else if (Array.isArray(res.data)) {
            setSessions(res.data);
          } else {
            setSessions([res.data]);
          }
        } catch (error: any) {
          console.error('Failed to fetch sessions', error);
          if (error.response?.status === 400) {
            setSessions([]);
          }
        } finally {
          setLoadingSessions(false);
        }
      };
      fetchSessions();
    }
  }, [activeTab, sessions.length]);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPassLoading(true);
    setPassStatus({ type: 'idle', msg: '' });
    try {
      await apiClient.patch('/auth/reset-password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      setPassStatus({ type: 'success', msg: 'Password updated successfully' });
      setCurrentPassword('');
      setNewPassword('');
    } catch (err: any) {
      setPassStatus({ 
        type: 'error', 
        msg: err.response?.data?.detail || 'Failed to update password' 
      });
    } finally {
      setPassLoading(false);
    }
  };

  return (
    <div className="mt-8 w-full max-w-3xl mx-auto flex flex-col gap-6 min-h-[60vh] px-4 pb-12">
      <h2 className="title text-3xl mb-2">Settings</h2>

      {/* Accordion Item: Profile */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <button 
          onClick={() => toggleTab('profile')}
          className="w-full flex items-center justify-between p-6 bg-transparent hover:bg-gray-50 border-none text-left cursor-pointer"
          style={{ transition: 'background-color 0.2s' }}
        >
          <div className="flex items-center gap-3">
            <UserIcon size={24} className="text-primary" />
            <span className="text-lg font-bold">Profile Information</span>
          </div>
          <div style={{ transform: activeTab === 'profile' ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s' }}>
            <ChevronDown size={24} className="text-gray-400" />
          </div>
        </button>
        
        <div className={`accordion-content ${activeTab === 'profile' ? 'expanded' : ''}`}>
          <div className="px-6 pb-6 pt-2 border-t border-gray-100">
            <div className="space-y-6 mt-4">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">Email Address</p>
                <p className="text-lg text-gray-900">{user?.email}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">Account Status</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`w-2.5 h-2.5 rounded-full ${user?.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  <span className="text-gray-900">{user?.is_active ? 'Active' : 'Inactive'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Accordion Item: Security */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <button 
          onClick={() => toggleTab('security')}
          className="w-full flex items-center justify-between p-6 bg-transparent hover:bg-gray-50 border-none text-left cursor-pointer"
          style={{ transition: 'background-color 0.2s' }}
        >
          <div className="flex items-center gap-3">
            <KeyRound size={24} className="text-primary" />
            <span className="text-lg font-bold">Security & Password</span>
          </div>
          <div style={{ transform: activeTab === 'security' ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s' }}>
            <ChevronDown size={24} className="text-gray-400" />
          </div>
        </button>
        
        <div className={`accordion-content ${activeTab === 'security' ? 'expanded' : ''}`}>
          <div className="px-6 pb-6 pt-2 border-t border-gray-100">
            <div className="mt-4 flex flex-col gap-8">
              <div>
                <h3 className="text-md font-semibold mb-4 text-gray-800">Change Password</h3>
                <form onSubmit={handlePasswordChange} className="max-w-md">
                  <Input
                    label="Current Password"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    required
                    placeholder="••••••••"
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
                  
                  {passStatus.type === 'success' && (
                    <p className="success-text mb-4 text-sm">{passStatus.msg}</p>
                  )}
                  {passStatus.type === 'error' && (
                    <p className="error-text mb-4 text-sm">{passStatus.msg}</p>
                  )}

                  <Button type="submit" variant="primary" className="mt-2" isLoading={passLoading}>
                    Update Password
                  </Button>
                </form>
              </div>

              <div className="border-t border-gray-100 pt-6">
                <h3 className="text-md font-semibold mb-2 text-gray-800">Set a Password</h3>
                <p className="text-sm text-gray-500 mb-6">
                  If you signed up using Google and don't have a password, you can set one here.
                </p>
                <form onSubmit={handleAddPassword} className="max-w-md">
                  <Input
                    label="New Password"
                    type="password"
                    value={addPasswordText}
                    onChange={(e) => setAddPasswordText(e.target.value)}
                    required
                    placeholder="••••••••"
                    minLength={8}
                  />
                  
                  {addPassStatus.type === 'success' && (
                    <p className="success-text mb-4 text-sm">{addPassStatus.msg}</p>
                  )}
                  {addPassStatus.type === 'error' && (
                    <p className="error-text mb-4 text-sm">{addPassStatus.msg}</p>
                  )}

                  <Button type="submit" variant="outline" className="mt-2" isLoading={addPassLoading}>
                    Add Password
                  </Button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Accordion Item: Sessions */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <button 
          onClick={() => toggleTab('sessions')}
          className="w-full flex items-center justify-between p-6 bg-transparent hover:bg-gray-50 border-none text-left cursor-pointer"
          style={{ transition: 'background-color 0.2s' }}
        >
          <div className="flex items-center gap-3">
            <Monitor size={24} className="text-primary" />
            <span className="text-lg font-bold">Active Sessions</span>
          </div>
          <div style={{ transform: activeTab === 'sessions' ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s' }}>
            <ChevronDown size={24} className="text-gray-400" />
          </div>
        </button>
        
        <div className={`accordion-content ${activeTab === 'sessions' ? 'expanded' : ''}`}>
          <div className="px-6 pb-6 pt-2 border-t border-gray-100">
            <div className="mt-4">
              {loadingSessions ? (
                <div className="flex justify-center p-8">
                  <Loader2 className="animate-spin text-blue-600" size={32} />
                </div>
              ) : sessions.length > 0 ? (
                <div className="space-y-4">
                  {sessions.map((session, index) => {
                    const isMobile = session.device_type?.toLowerCase().includes('mobile') || session.device_type?.toLowerCase() === 'phone';
                    const deviceName = session.device_name || session.device_type || 'Unknown Device';
                    
                    let lastSeenText = 'Unknown';
                    if (session.last_seen) {
                      try {
                        const date = new Date(typeof session.last_seen === 'number' && session.last_seen < 1e12 ? session.last_seen * 1000 : session.last_seen);
                        lastSeenText = date.toLocaleString();
                      } catch (e) {
                        lastSeenText = String(session.last_seen);
                      }
                    }

                    return (
                      <div key={index} className="flex items-center justify-between p-5 rounded-xl border border-gray-100 hover:border-gray-200 transition-colors bg-gray-50/50">
                        <div className="flex items-center gap-4">
                          <div className="p-3 border rounded-full bg-white text-gray-600 shadow-sm">
                            {isMobile ? <Smartphone size={24} /> : <Monitor size={24} />}
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900">
                              {deviceName}
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                              Last seen: {lastSeenText}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-semibold px-3 py-1.5 rounded-full border border-green-200 text-green-700 bg-green-50 inline-block mt-0 shadow-sm">
                            Active
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center p-8 text-gray-500 border-2 border-dashed border-gray-200 rounded-xl">
                  <Monitor size={48} className="mx-auto text-gray-300 mb-4" />
                  <p>No active sessions found.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};
