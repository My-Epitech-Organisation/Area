/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** dashboard
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConnectedServices } from '../hooks/useOAuth';
import { useAuthCheck } from '../hooks/useAuthCheck';
import type { Service, User } from '../types';
import { getStoredUser, getAccessToken, fetchUserData, API_BASE } from '../utils/helper';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import type { TooltipItem } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import EmailVerificationBanner from '../components/EmailVerificationBanner';

ChartJS.register(ArcElement, Tooltip, Legend);

interface ServiceUsageChartProps {
  services: Service[];
  activeServices: string[];
}

const ServiceUsageChart: React.FC<ServiceUsageChartProps> = ({ services, activeServices }) => {
  const usedServicesCount = activeServices.length;
  const totalServicesCount = services.length;
  const unusedServicesCount = totalServicesCount - usedServicesCount;

  const data = {
    labels: ['Used Services', 'Unused Services'],
    datasets: [
      {
        data: [usedServicesCount, unusedServicesCount],
        backgroundColor: ['#6366f1', '#4b5563'],
        borderColor: ['#4f46e5', '#374151'],
        borderWidth: 1,
        hoverBackgroundColor: ['#4f46e5', '#6b7280'],
        hoverBorderColor: ['#4338ca', '#4b5563'],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#e2e8f0',
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: function (context: TooltipItem<'doughnut'>) {
            const label = context.label || '';
            const value = typeof context.raw === 'number' ? context.raw : 0;
            const total = context.dataset.data.reduce((acc: number, val: number) => acc + val, 0);
            const percentage = Math.round((value / total) * 100);
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
  };

  return <Doughnut data={data} options={options} />;
};

const imageModules = import.meta.glob('../assets/*.{png,jpg,jpeg,svg,gif}', {
  eager: true,
}) as Record<string, { default: string }>;
const imagesByName: Record<string, string> = {};

Object.keys(imageModules).forEach((p) => {
  const parts = p.split('/');
  const file = parts[parts.length - 1];
  const name = file.replace(/\.[^/.]+$/, '').toLowerCase();
  imagesByName[name] = (imageModules as Record<string, { default: string }>)[p].default;
});

const Dashboard: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [activeServices, setActiveServices] = useState<string[]>([]);
  const { services: connectedServices, loading: connectedLoading } = useConnectedServices();

  // Verify authentication status on page load
  useAuthCheck();

  const normalizeServiceName = (name: string | null | undefined): string => {
    return (name || '')
      .toString()
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '');
  };

  useEffect(() => {
    if (!services || services.length === 0) return;

    const internalDefaults = new Set(['timer', 'debug', 'weather', 'email']);

    // Map service names to OAuth provider names
    const serviceToProviderMap: Record<string, string> = {
      'gmail': 'google',
      'googlecalendar': 'google',
      'youtube': 'google',
      'github': 'github',
      'slack': 'slack',
      'notion': 'notion',
      'spotify': 'spotify',
      'twitch': 'twitch',
    };

    const connectedProviders = new Set<string>();
    if (connectedServices && connectedServices.length > 0) {
      connectedServices.forEach((c) => {
        if (!c.is_expired) connectedProviders.add(normalizeServiceName(c.service_name));
      });
    }

    const active: string[] = [];
    services.forEach((s) => {
      const normalizedServiceName = normalizeServiceName(s.name);

      // Check if it's an internal service (always active)
      if (internalDefaults.has(normalizedServiceName)) {
        active.push(s.name);
        return;
      }

      // Get the OAuth provider for this service
      const oauthProvider = serviceToProviderMap[normalizedServiceName] || normalizedServiceName;

      // Check if user is connected to the provider
      if (connectedProviders.has(oauthProvider)) {
        active.push(s.name);
      }
    });

    setActiveServices(active);
  }, [services, connectedServices, connectedLoading]);
  const [_, setUserAreas] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const getServiceLogo = (service: Service): string | null => {
    if (service.logo) {
      const l = service.logo;
      if (l.startsWith('//')) return `https:${l}`;
      return l;
    }

    const key = service.name.toLowerCase();
    return imagesByName[key] || null;
  };

  const sortedServices = React.useMemo(() => {
    const sorted = [...services];
    const activeSet = new Set(activeServices.map((s) => (s || '').toString().toLowerCase()));
    sorted.sort((a, b) => {
      const aActive = activeSet.has((a.name || '').toString().toLowerCase()) ? 0 : 1;
      const bActive = activeSet.has((b.name || '').toString().toLowerCase()) ? 0 : 1;
      if (aActive !== bActive) return aActive - bActive;
      return (a.name || '').localeCompare(b.name || '');
    });
    return sorted;
  }, [services, activeServices]);

  const handleServiceClick = (serviceName: string) => {
    navigate(`/services/${serviceName.toLowerCase()}`);
  };

  useEffect(() => {
    setUser(null);

    const storedUser = getStoredUser();
    const accessToken = getAccessToken();
    const storedUsername = localStorage.getItem('username');
    const storedEmail = localStorage.getItem('email');

    if (accessToken && !storedUser) {
      const tempUser = {
        name: storedUsername || storedEmail || 'User',
        username: storedUsername || 'User',
        email: storedEmail || 'user@example.com',
        id: 'temp',
      };
      setUser(tempUser);
    }

    interface TokenPayload {
      user_id?: string;
      username?: string;
      email?: string;
      [key: string]: unknown;
    }

    const extractUserFromToken = (token: string): TokenPayload | null => {
      try {
        const base64Url = token.split('.')[1];
        if (!base64Url) return null;

        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
          atob(base64)
            .split('')
            .map(function (c) {
              return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            })
            .join('')
        );

        return JSON.parse(jsonPayload) as TokenPayload;
      } catch (e) {
        console.error('Error parsing JWT token:', e);
        return null;
      }
    };

    const loadUserData = async () => {
      if (accessToken) {
        try {
          const userToStore = await fetchUserData();
          if (userToStore) {
            setUser(userToStore);
          } else {
            if (accessToken) {
              const tokenData = extractUserFromToken(accessToken);
              if (tokenData && tokenData.user_id) {
                const userId = tokenData.user_id;
                let username = null;
                const refreshToken = localStorage.getItem('refresh');
                if (refreshToken) {
                  try {
                    const refreshTokenData = extractUserFromToken(refreshToken);
                    if (refreshTokenData && (refreshTokenData.username || refreshTokenData.email)) {
                      username = refreshTokenData.username || refreshTokenData.email;
                    }
                  } catch (e) {
                    console.error('Error extracting data from refresh token:', e);
                  }
                }
                try {
                  const userDetailResponse = await fetch(`${API_BASE}/auth/me/`, {
                    headers: {
                      Authorization: `Bearer ${accessToken}`,
                    },
                  });
                  if (userDetailResponse.ok) {
                    const userDetailData = await userDetailResponse.json();
                    const userFromDetail = {
                      name:
                        userDetailData.username ||
                        userDetailData.email ||
                        username ||
                        `User ${userId.substring(0, 6)}`,
                      username:
                        userDetailData.username || username || `User ${userId.substring(0, 6)}`,
                      email: userDetailData.email,
                      email_verified: userDetailData.email_verified || false,
                      id: userId,
                    };
                    localStorage.setItem('user', JSON.stringify(userFromDetail));
                    setUser(userFromDetail);
                  } else {
                    const displayName = username || `User ${userId.substring(0, 6)}`;
                    const userFromToken = {
                      name: displayName,
                      username: displayName,
                      id: userId,
                    };
                    localStorage.setItem('user', JSON.stringify(userFromToken));
                    setUser(userFromToken);
                  }
                } catch (error) {
                  console.error('Failed to fetch user details:', error);
                  const displayName = username || `User ${userId.substring(0, 6)}`;
                  const userFromToken = {
                    name: displayName,
                    username: displayName,
                    id: userId,
                  };
                  localStorage.setItem('user', JSON.stringify(userFromToken));
                  setUser(userFromToken);
                }
              }
            }
          }
        } catch (error) {
          console.error('Failed to fetch user data:', error);
          if (accessToken) {
            const tokenData = extractUserFromToken(accessToken);
            if (tokenData && tokenData.user_id) {
              const userId = tokenData.user_id;
              let username = null;
              const refreshToken = localStorage.getItem('refresh');
              if (refreshToken) {
                try {
                  const refreshTokenData = extractUserFromToken(refreshToken);
                  if (refreshTokenData && (refreshTokenData.username || refreshTokenData.email)) {
                    username = refreshTokenData.username || refreshTokenData.email;
                  }
                } catch (e) {
                  console.error('Error extracting data from refresh token (fallback):', e);
                }
              }
              const displayName = username || `User ${userId.substring(0, 6)}`;
              const userFromToken = {
                name: displayName,
                username: displayName,
                id: userId,
              };
              localStorage.setItem('user', JSON.stringify(userFromToken));
              setUser(userFromToken);
            }
          }
        }
      } else if (storedUser) {
        // Use stored user temporarily while we fetch fresh data
        setUser(storedUser);
      }
    };

    const fetchData = async () => {
      setLoading(true);
      try {
        // Always fetch fresh user data to ensure email_verified is up-to-date
        await loadUserData();
        const servicesResponse = await fetch(`${API_BASE}/about.json`);
        if (!servicesResponse.ok) {
          throw new Error(`HTTP Error: ${servicesResponse.status}`);
        }
        const servicesData = await servicesResponse.json();
        const servicesList = servicesData?.server?.services || [];
        const formattedServices = servicesList.map(
          (s: {
            name: string;
            actions?: unknown[];
            reactions?: unknown[];
            logo?: string | null;
          }) => ({
            name: s.name,
            actions: s.actions || [],
            reactions: s.reactions || [],
            logo: s.logo || null,
          })
        );
        setServices(formattedServices);

        const isFullyAuthenticated = () => {
          return (
            storedUser &&
            accessToken &&
            storedUser.id &&
            (storedUser.username || storedUser.name || storedUser.email)
          );
        };
        if (isFullyAuthenticated()) {
          try {
            // Note: activeServices is now managed by the useEffect that watches connectedServices
            // This ensures the Service Usage chart always reflects real OAuth connections
            const fetchWithTimeout = async (url: string, options: RequestInit, timeout: number) => {
              const controller = new AbortController();
              const { signal } = controller;
              const timeoutId = setTimeout(() => controller.abort(), timeout);
              try {
                const response = await fetch(url, { ...options, signal });
                clearTimeout(timeoutId);
                return response;
              } catch (error) {
                clearTimeout(timeoutId);
                throw error;
              }
            };

            const areasResponse = await fetchWithTimeout(
              `${API_BASE}/api/areas/`,
              {
                headers: {
                  Authorization: `Bearer ${accessToken}`,
                  'Content-Type': 'application/json',
                },
              },
              5000
            ).catch((error) => {
              if (error.name === 'AbortError') {
                console.error('Areas fetch timed out');
              } else {
                console.error('Areas fetch failed:', error.message);
              }
              return null;
            });

            if (areasResponse && areasResponse.ok) {
              const areasData = await areasResponse.json();
              setUserAreas(areasData);
              // Note: We no longer update activeServices here
              // It's automatically calculated by the useEffect watching connectedServices
            }
          } catch {
            // Error fetching areas - activeServices is still managed by connectedServices useEffect
          }
        }
        // Note: For non-authenticated users, activeServices will be empty or contain only internal services
        // This is handled by the useEffect that watches connectedServices
        setError(null);
      } catch (err: unknown) {
        console.error('Failed to fetch services:', err);
        setError(err instanceof Error ? err.message : 'Failed to load services');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [navigate]);

  const handleRefreshUserData = async () => {
    try {
      const updatedUser = await fetchUserData();
      if (updatedUser) {
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
      }
    } catch (err) {
      console.error('Error refreshing user data:', err);
    }
  };

  useEffect(() => {
    const handleFocus = () => {
      handleRefreshUserData();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  return (
    <div className="w-full min-h-screen bg-dashboard flex flex-col md:flex-row pt-16">
      <div className="flex flex-1">
        <div className="flex-1 p-4 md:p-6 flex flex-col items-center overflow-y-auto">
          <header className="w-full flex flex-col items-center pt-4 mb-4">
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-center text-theme-primary mb-2">
              Dashboard
            </h1>
            <div className="w-full flex items-center justify-center">
              {user ? (
                <p className="text-xl md:text-2xl lg:text-3xl font-semibold text-theme-accent mt-2 animate-fadeIn">
                  Welcome back, {user.username || user.name}!
                </p>
              ) : (
                <p className="text-lg md:text-xl lg:text-2xl font-semibold text-amber-400 mt-2 animate-pulse">
                  <span
                    onClick={() => navigate('/login')}
                    className="cursor-pointer hover:underline"
                  >
                    Sign in to unlock all features
                  </span>
                </p>
              )}
            </div>
          </header>

          {/* Email Verification Banner */}
          <EmailVerificationBanner user={user} onVerificationSent={handleRefreshUserData} />

          <div className="w-full flex flex-col gap-4 mb-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-theme-primary">
                <h2 className="text-xl font-semibold text-theme-accent mb-3">Services Usage</h2>
                <div className="flex justify-center h-32 md:h-[180px]">
                  <ServiceUsageChart services={services} activeServices={activeServices} />
                </div>
              </div>
              <div className="bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-theme-primary">
                <h2 className="text-xl font-semibold text-theme-accent mb-3">Quick Actions</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button
                    onClick={() => navigate('/Areaction')}
                    className="bg-gradient-to-br from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 border-2 border-indigo-400 text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-2xl hover:scale-105 transform"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-10 w-10 mb-2"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                      />
                    </svg>
                    <span className="font-semibold text-base">New Automation</span>
                  </button>
                  <button
                    onClick={() => navigate('/Areaction')}
                    className="bg-gradient-to-br from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800 border-2 border-pink-400 text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-2xl hover:scale-105 transform"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-10 w-10 mb-2"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414a1 1 0 00-.707-.293H4"
                      />
                    </svg>
                    <span className="font-semibold text-base">My Automations</span>
                  </button>
                  <button
                    onClick={() => navigate('/debug')}
                    className="bg-gradient-to-br from-cyan-600 to-cyan-700 hover:from-cyan-700 hover:to-cyan-800 border-2 border-cyan-400 text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-2xl hover:scale-105 transform"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-10 w-10 mb-2"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                      />
                    </svg>
                    <span className="font-semibold text-base">Test Your Automations</span>
                  </button>
                  <button
                    onClick={() => navigate('/profile')}
                    className="bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 border-2 border-purple-400 text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-2xl hover:scale-105 transform"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-10 w-10 mb-2"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2a1 1 0 001 1h14a1 1 0 001-1v-2c0-2.66-5.33-4-8-4z"
                      />
                    </svg>
                    <span className="font-semibold text-base">View Profile</span>
                  </button>
                </div>
              </div>
            </div>
            <div className="bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-gray-200">
              <h2 className="text-xl font-semibold text-indigo-300 mb-3">Services</h2>
              {loading ? (
                <div className="flex justify-center items-center h-40">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
                </div>
              ) : error ? (
                <div className="text-center py-10">
                  <p className="text-red-400 mb-2">Error loading services</p>
                  <p className="text-sm text-gray-400">{error}</p>
                </div>
              ) : services.length === 0 ? (
                <div className="text-center py-10">
                  <p className="text-gray-400">No services available</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
                  {sortedServices.map((service) => {
                    // Check if user is connected to this service
                    const normalizedServiceName = normalizeServiceName(service.name);

                    // Internal services that don't require OAuth (always active)
                    const internalServices = new Set(['timer', 'debug', 'weather', 'email']);
                    const isInternalService = internalServices.has(normalizedServiceName);

                    // Map service names to OAuth provider names
                    // Gmail, Calendar, YouTube all use "google" OAuth
                    const serviceToProviderMap: Record<string, string> = {
                      'gmail': 'google',
                      'googlecalendar': 'google',  // normalized from google_calendar
                      'youtube': 'google',
                      'github': 'github',
                      'slack': 'slack',
                      'notion': 'notion',
                      'spotify': 'spotify',
                      'twitch': 'twitch',
                    };

                    // Get the OAuth provider name for this service
                    const oauthProvider = serviceToProviderMap[normalizedServiceName] || normalizedServiceName;

                    // Check if service is in connectedServices
                    const isConnected = connectedServices?.some(
                      (c) => normalizeServiceName(c.service_name) === oauthProvider && !c.is_expired
                    ) ?? false;

                    // Service is active if it's internal OR user is connected to it
                    const isActive = isInternalService || isConnected;

                    const logo = getServiceLogo(service);
                    return (
                      <div
                        key={service.name}
                        onClick={() => handleServiceClick(service.name)}
                        className="bg-white bg-opacity-10 rounded-xl p-3 cursor-pointer transform transition-all duration-300 hover:bg-opacity-20 hover:scale-105 hover:shadow-lg flex flex-col items-center text-center"
                      >
                        <div className="w-16 h-16 rounded-full bg-white bg-opacity-10 flex items-center justify-center overflow-hidden mb-2">
                          {logo ? (
                            <img
                              src={logo}
                              alt={`${service.name} logo`}
                              className="w-12 h-12 object-contain"
                              style={
                                ['timer', 'debug', 'email', 'weather'].includes(
                                  service.name.toLowerCase()
                                )
                                  ? {
                                      filter:
                                        'drop-shadow(0 0 1px rgba(255,255,255,0.6)) drop-shadow(0 0 2px rgba(255,255,255,0.4))',
                                    }
                                  : undefined
                              }
                            />
                          ) : (
                            <div className="text-2xl font-bold text-white opacity-50">
                              {service.name.charAt(0)}
                            </div>
                          )}
                        </div>
                        <h3 className="text-sm font-semibold text-white mb-2 line-clamp-1">
                          {service.name}
                        </h3>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${isActive ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}
                        >
                          {isActive ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
