import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStoredUser, getAccessToken, fetchUserData, API_BASE } from '../utils/helper';
import type { User } from '../types';
import ProfileModal from '../components/ProfileModal';

const Profile: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [sendingVerification, setSendingVerification] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [sendingPasswordReset, setSendingPasswordReset] = useState(false);
  interface ProfileUpdate {
    username?: string;
    email?: string;
    password?: string;
  }

  const [pendingProfileUpdate, setPendingProfileUpdate] = useState<ProfileUpdate | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUserProfile = async () => {
      setLoading(true);
      const storedUser = getStoredUser();
      const accessToken = getAccessToken();

      if (!accessToken) {
        navigate('/login');
        return;
      }

      if (storedUser) {
        setUser(storedUser);
        setUsername(storedUser.username || '');
        setEmail(storedUser.email || '');
      }

      try {
        const updatedUser = await fetchUserData();

        if (updatedUser) {
          setUser(updatedUser);
          setUsername(updatedUser.username || '');
          setEmail(updatedUser.email || '');
          // Update localStorage with fresh data
          localStorage.setItem('user', JSON.stringify(updatedUser));
        } else if (!storedUser) {
          navigate('/login');
        }
      } catch (err) {
        console.error('Error loading profile data:', err);
        setError('Failed to load profile data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadUserProfile();
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setSaving(true);
    const accessToken = getAccessToken();

    if (!accessToken) {
      setError('You must be logged in to update your profile');
      setSaving(false);
      return;
    }

    const updateData: Record<string, string> = {};

    if (username && username !== user?.username) {
      updateData.username = username;
    }

    if (email && email !== user?.email) {
      updateData.email = email;
    }

    if (password) {
      updateData.password = password;
    }

    if (Object.keys(updateData).length === 0) {
      setSuccess('No changes to save');
      setSaving(false);
      return;
    }

    setPendingProfileUpdate(updateData);
    setIsPasswordModalOpen(true);
    setSaving(false);
    return;
  };

  const handlePasswordConfirm = async (oldPassword: string) => {
    if (!oldPassword || !pendingProfileUpdate) return;

    setSaving(true);
    const accessToken = getAccessToken();

    try {
      let hasUpdates = false;
      let successMessage = '';

      if (pendingProfileUpdate?.password) {
        const passwordResponse = await fetch(`${API_BASE}/auth/password/change/`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            old_password: oldPassword,
            new_password: pendingProfileUpdate.password,
            confirm_password: pendingProfileUpdate.password,
          }),
        });

        if (passwordResponse.ok) {
          hasUpdates = true;
          successMessage = 'Password updated successfully. ';

          try {
            const refreshedUser = await fetchUserData();
            if (refreshedUser) {
              setUser(refreshedUser);
            }
          } catch (refreshErr) {
            console.warn('Could not refresh user data after password update:', refreshErr);
          }
        } else {
          const errorData = await passwordResponse.json().catch(() => ({}));
          setError(
            errorData.detail ||
              'Failed to update password. Password change may require your current password.'
          );
          setSaving(false);
          setPendingProfileUpdate(null);
          setIsPasswordModalOpen(false);
          return;
        }
      }

      const newUsername = pendingProfileUpdate?.username;
      const newEmail = pendingProfileUpdate?.email;

      if (
        (newUsername && newUsername !== user?.username) ||
        (newEmail && newEmail !== user?.email)
      ) {
        try {
          const profileResponse = await fetch(`${API_BASE}/auth/me/`, {
            method: 'PUT',
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: newUsername || user?.username,
              email: newEmail || user?.email,
            }),
          });

          if (profileResponse.ok) {
            if (user) {
              const updatedUser: User = {
                name: newUsername || user.name,
                username: newUsername || user.username,
                email: newEmail || user.email,
                id: user.id,
              };

              localStorage.setItem('user', JSON.stringify(updatedUser));
              if (newUsername) localStorage.setItem('username', newUsername);
              if (newEmail) localStorage.setItem('email', newEmail);
              setUser(updatedUser);
              hasUpdates = true;

              successMessage += 'Profile updated successfully. ';
            }
          } else {
            const errorData = await profileResponse.json().catch(() => ({}));
            const errorMessage =
              errorData.detail ||
              errorData.email?.[0] ||
              errorData.username?.[0] ||
              'Failed to update profile information.';

            setError(errorMessage);
            setSaving(false);
            setPendingProfileUpdate(null);
            setIsPasswordModalOpen(false);
            return;
          }
        } catch (err) {
          console.error('Failed to update profile on server:', err);
          setError('Connection error: Failed to update profile. Please try again later.');
          setSaving(false);
          return;
        }
      }

      setPassword('');
      setConfirmPassword('');

      if (hasUpdates) {
        setSuccess(successMessage);
      } else {
        setSuccess('No changes to save');
      }

      setPendingProfileUpdate(null);
      setIsPasswordModalOpen(false);

      if (!error) {
        setIsEditMode(false);
      }
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('An error occurred while updating your profile. Please try again.');
      setPendingProfileUpdate(null);
      setIsPasswordModalOpen(false);
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    if (user) {
      setUsername(user.username || '');
      setEmail(user.email || '');
    }
    setPassword('');
    setConfirmPassword('');
    setIsEditMode(false);
    setError(null);
  };

  const handleResendVerification = async () => {
    if (!user?.email) return;

    setSendingVerification(true);
    setError(null);
    setSuccess(null);

    const accessToken = getAccessToken();

    if (!accessToken) {
      setError('You must be logged in to resend verification email');
      setSendingVerification(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/auth/send-verification-email/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: user.email }),
      });

      if (response.ok) {
        setSuccess('Verification email sent! Please check your inbox.');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.error || errorData.detail || 'Failed to send verification email. Please try again.');
      }
    } catch (err) {
      console.error('Error sending verification email:', err);
      setError('Failed to send verification email. Please try again.');
    } finally {
      setSendingVerification(false);
    }
  };

  const handleRefreshStatus = async () => {
    setRefreshing(true);
    setError(null);
    setSuccess(null);

    try {
      const updatedUser = await fetchUserData();

      if (updatedUser) {
        setUser(updatedUser);
        setUsername(updatedUser.username || '');
        setEmail(updatedUser.email || '');
        // Update localStorage with fresh data
        localStorage.setItem('user', JSON.stringify(updatedUser));

        if (updatedUser.email_verified) {
          setSuccess('Email verification status updated! Your email is now verified.');
        }
      }
    } catch (err) {
      console.error('Error refreshing user data:', err);
      setError('Failed to refresh status. Please try again.');
    } finally {
      setRefreshing(false);
    }
  };

  const handlePasswordReset = async () => {
    if (!user?.email) return;

    setSendingPasswordReset(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_BASE}/auth/password-reset/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: user.email }),
      });

      if (response.ok) {
        setSuccess('Password reset email sent! Please check your inbox for instructions.');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.error || errorData.detail || 'Failed to send password reset email. Please try again.');
      }
    } catch (err) {
      console.error('Error sending password reset email:', err);
      setError('Failed to send password reset email. Please try again.');
    } finally {
      setSendingPasswordReset(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-profile flex flex-col items-center">
      <ProfileModal
        isOpen={isPasswordModalOpen}
        onClose={() => {
          setIsPasswordModalOpen(false);
          setPendingProfileUpdate(null);
          setSaving(false);
        }}
        onConfirm={handlePasswordConfirm}
        title="Confirm Profile Changes"
        message="Please enter your current password to save your changes"
      />
      <header className="w-full pt-20 pb-6 flex justify-center">
        <h1 className="text-4xl md:text-5xl font-bold text-theme-primary">Your Profile</h1>
      </header>
      <main className="w-full max-w-3xl px-4 flex-1 flex flex-col items-center pb-12">
        {loading ? (
          <div className="flex justify-center items-center h-40">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        ) : (
          <div className="w-full bg-white/5 p-8 rounded-xl backdrop-blur-sm border border-white/10 shadow-xl animate-appear">
            {error && (
              <div className="mb-6 p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-200 animate-slide-up">
                {error}
              </div>
            )}

            {success && (
              <div className="mb-6 p-3 bg-green-500/20 border border-green-500/30 rounded-lg text-green-200 animate-slide-up">
                {success}
              </div>
            )}

            <div className="flex items-center gap-6 mb-8">
              <div className="w-24 h-24 bg-gradient-avatar rounded-full flex items-center justify-center text-white text-4xl font-bold shadow-lg transition-transform duration-300 hover:scale-105">
                {user?.username?.[0]?.toUpperCase() || user?.name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{user?.username || user?.name}</h2>
                <div className="flex items-center gap-2">
                  <p className="text-indigo-300">{user?.email}</p>
                  {user?.email_verified && (
                    <svg
                      className="w-5 h-5 text-green-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <title>Email verified</title>
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              </div>
            </div>

            {isEditMode ? (
              <>
                <h3 className="text-xl font-semibold text-white mb-6">Edit Profile Information</h3>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-4">
                    <div>
                      <label
                        htmlFor="username"
                        className="block text-sm font-medium text-indigo-200 mb-1"
                      >
                        Username
                      </label>
                      <input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="Username"
                      />
                    </div>
                    <div>
                      <label
                        htmlFor="email"
                        className="block text-sm font-medium text-indigo-200 mb-1"
                      >
                        Email Address
                      </label>
                      <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="Email address"
                      />
                    </div>
                    <div>
                      <label
                        htmlFor="password"
                        className="block text-sm font-medium text-indigo-200 mb-1"
                      >
                        New Password (leave blank to keep current)
                      </label>
                      <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="New password"
                      />
                    </div>
                    <div>
                      <label
                        htmlFor="confirmPassword"
                        className="block text-sm font-medium text-indigo-200 mb-1"
                      >
                        Confirm New Password
                      </label>
                      <input
                        id="confirmPassword"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="Confirm new password"
                      />
                    </div>
                  </div>
                  <div className="pt-4 flex gap-4">
                    <button
                      type="button"
                      onClick={handleCancelEdit}
                      className="w-1/2 py-3 px-6 rounded-lg bg-gray-600 hover:bg-gray-500 text-white font-medium text-lg transition-all duration-300"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={saving}
                      className={`w-1/2 py-3 px-6 rounded-lg bg-gradient-button-primary hover:bg-gradient-button-primary text-white font-medium text-lg transition-all duration-300 ${saving ? 'opacity-70 cursor-not-allowed' : ''}`}
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </form>
              </>
            ) : (
              <>
                <h3 className="text-xl font-semibold text-white mb-6">Profile Information</h3>
                <div className="space-y-6">
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-indigo-200 mb-1">Username</h4>
                      <p className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white">
                        {user?.username || 'Not set'}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-indigo-200 mb-1">Email Address</h4>
                      <div className="space-y-2">
                        <p className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white">
                          {user?.email || 'Not set'}
                        </p>
                        {user?.email && (
                          <div className="flex items-center justify-between px-4 py-2 bg-white/5 border border-white/10 rounded-lg">
                            <div className="flex items-center gap-2">
                              {user.email_verified ? (
                                <>
                                  <svg
                                    className="w-5 h-5 text-green-400"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                  >
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth={2}
                                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                    />
                                  </svg>
                                  <span className="text-sm text-green-400 font-medium">
                                    Email Verified
                                  </span>
                                </>
                              ) : (
                                <>
                                  <svg
                                    className="w-5 h-5 text-yellow-400"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                  >
                                    <path
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth={2}
                                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                    />
                                  </svg>
                                  <span className="text-sm text-yellow-400 font-medium">
                                    Email Not Verified
                                  </span>
                                </>
                              )}
                            </div>
                            {!user.email_verified && (
                              <div className="flex gap-2">
                                <button
                                  onClick={handleResendVerification}
                                  disabled={sendingVerification}
                                  className="px-3 py-1 text-xs rounded-md bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  {sendingVerification ? 'Sending...' : 'Resend Email'}
                                </button>
                                <button
                                  onClick={handleRefreshStatus}
                                  disabled={refreshing}
                                  className="px-3 py-1 text-xs rounded-md bg-green-600 hover:bg-green-500 text-white font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                  title="Refresh verification status"
                                >
                                  {refreshing ? (
                                    'Refreshing...'
                                  ) : (
                                    <svg
                                      className="w-4 h-4"
                                      fill="none"
                                      stroke="currentColor"
                                      viewBox="0 0 24 24"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                                      />
                                    </svg>
                                  )}
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-indigo-200 mb-1">Password</h4>
                      <div className="space-y-2">
                        <p className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white">
                          ••••••••
                        </p>
                        <button
                          onClick={handlePasswordReset}
                          disabled={sendingPasswordReset}
                          className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-indigo-300 hover:bg-white/10 hover:text-indigo-200 transition-all duration-200 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {sendingPasswordReset ? (
                            <span className="flex items-center justify-center gap-2">
                              <svg
                                className="animate-spin h-4 w-4"
                                fill="none"
                                viewBox="0 0 24 24"
                              >
                                <circle
                                  className="opacity-25"
                                  cx="12"
                                  cy="12"
                                  r="10"
                                  stroke="currentColor"
                                  strokeWidth="4"
                                />
                                <path
                                  className="opacity-75"
                                  fill="currentColor"
                                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                />
                              </svg>
                              Sending Reset Email...
                            </span>
                          ) : (
                            <span className="flex items-center justify-center gap-2">
                              <svg
                                className="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
                                />
                              </svg>
                              Forgot Password? Send Reset Email
                            </span>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="pt-4">
                    <button
                      onClick={() => setIsEditMode(true)}
                      className="w-full py-3 px-6 rounded-lg bg-gradient-button-primary hover:bg-gradient-button-primary text-white font-medium text-lg transition-all duration-300"
                    >
                      Update Profile
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Profile;
