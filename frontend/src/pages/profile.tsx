import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getStoredUser, getAccessToken } from "../utils/helper";
import type { User } from "../types";

const API_BASE = (import.meta.env.VITE_API_BASE as string) || "http://localhost:8080";

const Profile: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      setLoading(true);
      const storedUser = getStoredUser();
      const accessToken = getAccessToken();
      if (!accessToken) {
        navigate("/login");
        return;
      }

      if (storedUser) {
        setUser(storedUser);
        setUsername(storedUser.username || "");
        setEmail(storedUser.email || "");
      }

      try {
        const response = await fetch(`${API_BASE}/auth/me/`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        });

        if (response.ok) {
          const userData = await response.json();
          const updatedUser = {
            name: userData.username || userData.email || "User",
            username: userData.username || "User",
            email: userData.email || "",
            id: userData.id || userData.pk
          };

          localStorage.setItem('user', JSON.stringify(updatedUser));
          setUser(updatedUser);
          setUsername(updatedUser.username || "");
          setEmail(updatedUser.email || "");
        } else {
          console.error("Failed to fetch user data:", await response.text());
          if (!storedUser) {
            navigate("/login");
          }
        }
      } catch (err) {
        console.error("Error fetching user profile:", err);
        setError("Failed to load profile data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setSaving(true);
    const accessToken = getAccessToken();

    if (!accessToken) {
      setError("You must be logged in to update your profile");
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
      setSuccess("No changes to save");
      setSaving(false);
      return;
    }

    try {
      let hasUpdates = false;
      let successMessage = "";

      const oldPassword = prompt("Please enter your current password to confirm changes");

      if (!oldPassword) {
        setError("Profile update cancelled - current password required");
        setSaving(false);
        return;
      }

      if (password) {
        const passwordResponse = await fetch(`${API_BASE}/auth/password/change/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            old_password: oldPassword,
            new_password: password,
            confirm_password: confirmPassword
          })
        });

        if (passwordResponse.ok) {
          hasUpdates = true;
          successMessage = "Password updated successfully. ";

          try {
            const userResponse = await fetch(`${API_BASE}/auth/me/`, {
              headers: {
                'Authorization': `Bearer ${accessToken}`
              }
            });

            if (userResponse.ok) {
              const userData = await userResponse.json();
              const refreshedUser = {
                name: userData.username || userData.email || "User",
                username: userData.username || "User",
                email: userData.email || "",
                id: userData.id || userData.pk
              };

              localStorage.setItem('user', JSON.stringify(refreshedUser));
              setUser(refreshedUser);
            }
          } catch (refreshErr) {
            console.warn("Could not refresh user data after password update:", refreshErr);
          }
        } else {
          const errorData = await passwordResponse.json().catch(() => ({}));
          setError(errorData.detail || "Failed to update password. Password change may require your current password.");
          setSaving(false);
          return;
        }
      }

      if ((username && username !== user?.username) || (email && email !== user?.email)) {
        try {
          await fetch(`${API_BASE}/auth/me/`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              username: username || user?.username,
              email: email || user?.email
            })
          });

          if (user) {
            const updatedUser: User = {
              name: username || user.name,
              username: username || user.username,
              email: email || user.email,
              id: user.id
            };

            localStorage.setItem('user', JSON.stringify(updatedUser));
            if (username) localStorage.setItem('username', username);
            if (email) localStorage.setItem('email', email);
            setUser(updatedUser);
            hasUpdates = true;

            successMessage += "Profile updated successfully. ";
          }
        } catch (err) {
          console.error("Failed to update profile on server:", err);

          if (user) {
            const updatedUser: User = {
              name: username || user.name,
              username: username || user.username,
              email: email || user.email,
              id: user.id
            };

            localStorage.setItem('user', JSON.stringify(updatedUser));
            if (username) localStorage.setItem('username', username);
            if (email) localStorage.setItem('email', email);
            setUser(updatedUser);
            hasUpdates = true;

            successMessage += "Changes saved locally. Server sync failed - changes may not persist after logout. ";
          }
        }
      }

      setPassword("");
      setConfirmPassword("");

      if (hasUpdates) {
        setSuccess(successMessage);
      } else {
        setSuccess("No changes to save");
      }
    } catch (err) {
      console.error("Error updating profile:", err);
      setError("An error occurred while updating your profile. Please try again.");
    } finally {
      setSaving(false);
      if (!error) {
        setIsEditMode(false);
      }
    }
  };

  const handleCancelEdit = () => {
    if (user) {
      setUsername(user.username || "");
      setEmail(user.email || "");
    }
    setPassword("");
    setConfirmPassword("");
    setIsEditMode(false);
    setError(null);
  };

  return (
    <div className="w-full min-h-screen bg-profile flex flex-col items-center">
      <header className="w-full pt-20 pb-6 flex justify-center">
        <h1 className="text-4xl md:text-5xl font-bold text-white">Your Profile</h1>
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
              <div className="w-24 h-24 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full flex items-center justify-center text-white text-4xl font-bold shadow-lg transition-transform duration-300 hover:scale-105">
                {user?.username?.[0]?.toUpperCase() || user?.name?.[0]?.toUpperCase() || "U"}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{user?.username || user?.name}</h2>
                <p className="text-indigo-300">{user?.email}</p>
              </div>
            </div>

            {isEditMode ? (
              <>
                <h3 className="text-xl font-semibold text-white mb-6">Edit Profile Information</h3>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="username" className="block text-sm font-medium text-indigo-200 mb-1">
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
                      <label htmlFor="email" className="block text-sm font-medium text-indigo-200 mb-1">
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
                      <label htmlFor="password" className="block text-sm font-medium text-indigo-200 mb-1">
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
                      <label htmlFor="confirmPassword" className="block text-sm font-medium text-indigo-200 mb-1">
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
                      className={`w-1/2 py-3 px-6 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-lg transition-all duration-300 ${saving ? 'opacity-70 cursor-not-allowed' : ''}`}
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
                        {user?.username || "Not set"}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-indigo-200 mb-1">Email Address</h4>
                      <p className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white">
                        {user?.email || "Not set"}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-indigo-200 mb-1">Password</h4>
                      <p className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white">
                        ••••••••
                      </p>
                    </div>
                  </div>
                  <div className="pt-4">
                    <button
                      onClick={() => setIsEditMode(true)}
                      className="w-full py-3 px-6 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-lg transition-all duration-300"
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
