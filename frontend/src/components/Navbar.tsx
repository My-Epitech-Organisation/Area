import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getStoredUser } from '../utils/helper';
import type { User } from '../types';

const Navbar: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const location = useLocation();

  useEffect(() => {
    const checkAndUpdateUser = () => {
      const currentUser = getStoredUser();
      if (JSON.stringify(currentUser) !== JSON.stringify(user)) {
        setUser(currentUser);
      }
    };

    checkAndUpdateUser();

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        checkAndUpdateUser();
      }
    };

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'user' || e.key === 'access' || e.key === null) {
        checkAndUpdateUser();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('storage', handleStorageChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [user, location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('access');
    localStorage.removeItem('access_token');
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
    localStorage.removeItem('username');
    localStorage.removeItem('email');

    setUser(null);

    window.location.replace('/homepage');
  };

  return (
    <nav className="w-full fixed top-0 left-0 z-50 bg-black/50 backdrop-blur-sm border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-16 flex items-center justify-center">
          <div className="flex items-center space-x-8">
            <Link
              to="/homepage"
              className="text-white text-lg font-semibold hover:text-indigo-300 transition"
            >
              Home
            </Link>
            <Link
              to="/Areaction"
              className="text-white text-lg font-semibold hover:text-indigo-300 transition"
            >
              Area
            </Link>
            <Link
              to="/services"
              className="text-white text-lg font-semibold hover:text-indigo-300 transition"
            >
              Services
            </Link>
            <Link
              to="/about"
              className="text-white text-lg font-semibold hover:text-indigo-300 transition"
            >
              About Us
            </Link>
            <Link
              to="/dashboard"
              className="text-white text-lg font-semibold hover:text-indigo-300 transition"
            >
              Dashboard
            </Link>
            <Link
              to="/profile"
              className="text-white text-lg font-semibold hover:text-indigo-300 transition"
            >
              Profile
            </Link>
          </div>
        </div>
      </div>

      <div className="absolute right-4 top-0 h-16 flex items-center space-x-8">
        {user ? (
          <>
            <span className="text-indigo-300 text-lg font-semibold">
              {user.username || user.name}
            </span>
            <button
              onClick={handleLogout}
              className="text-red-400 text-lg font-semibold hover:text-red-800 transition"
            >
              Log Out
            </button>
          </>
        ) : (
          <>
            <Link
              to="/login"
              className="text-white text-lg font-semibold hover:text-indigo-300 transition"
            >
              Log In
            </Link>
            <Link
              to="/signup"
              className="text-white text-lg font-semibold hover:text-indigo-300 transition"
            >
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
