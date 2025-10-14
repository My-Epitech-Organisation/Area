import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getStoredUser } from '../utils/helper';
import type { User } from '../types';

const Navbar: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
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
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="h-16 flex items-center justify-between">
          {/* Hamburger menu for mobile */}
          <button
            className="md:hidden text-white text-2xl focus:outline-none"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            ☰
          </button>

          {/* Desktop links */}
          <div className="hidden md:flex items-center space-x-4 lg:space-x-8">
            <Link
              to="/homepage"
              className="text-white text-sm lg:text-lg font-semibold hover:text-indigo-300 transition"
            >
              Home
            </Link>
            <Link
              to="/Areaction"
              className="text-white text-sm lg:text-lg font-semibold hover:text-indigo-300 transition"
            >
              Area
            </Link>
            <Link
              to="/services"
              className="text-white text-sm lg:text-lg font-semibold hover:text-indigo-300 transition"
            >
              Services
            </Link>
            <Link
              to="/about"
              className="text-white text-sm lg:text-lg font-semibold hover:text-indigo-300 transition"
            >
              About Us
            </Link>
            <Link
              to="/dashboard"
              className="text-white text-sm lg:text-lg font-semibold hover:text-indigo-300 transition"
            >
              Dashboard
            </Link>
            <Link
              to="/profile"
              className="text-white text-sm lg:text-lg font-semibold hover:text-indigo-300 transition"
            >
              Profile
            </Link>
          </div>

          {/* User actions */}
          <div className="flex items-center space-x-2 md:space-x-4 lg:space-x-8">
            {user ? (
              <>
                <span className="hidden sm:inline text-indigo-300 text-sm lg:text-lg font-semibold">
                  {user.username || user.name}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-white text-sm lg:text-lg font-semibold hover:text-red-400 transition"
                >
                  Log Out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-white text-sm lg:text-lg font-semibold hover:text-indigo-300 transition"
                >
                  Log In
                </Link>
                <Link
                  to="/signup"
                  className="text-white text-sm lg:text-lg font-semibold hover:text-indigo-300 transition"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Mobile menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-gradient-to-br from-indigo-800 via-black to-purple-600 backdrop-blur-sm border-t border-white/5">
            <div className="px-4 py-4 space-y-4">
              <Link
                to="/homepage"
                className="block text-white text-lg font-semibold hover:text-indigo-300 transition"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Home
              </Link>
              <Link
                to="/Areaction"
                className="block text-white text-lg font-semibold hover:text-indigo-300 transition"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Area
              </Link>
              <Link
                to="/services"
                className="block text-white text-lg font-semibold hover:text-indigo-300 transition"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Services
              </Link>
              <Link
                to="/about"
                className="block text-white text-lg font-semibold hover:text-indigo-300 transition"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                About Us
              </Link>
              <Link
                to="/dashboard"
                className="block text-white text-lg font-semibold hover:text-indigo-300 transition"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Dashboard
              </Link>
              <Link
                to="/profile"
                className="block text-white text-lg font-semibold hover:text-indigo-300 transition"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Profile
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
