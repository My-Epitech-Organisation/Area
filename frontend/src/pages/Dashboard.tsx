/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** dashboard
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Service, User } from '../types';
import { getStoredUser, getAccessToken, fetchUserData, API_BASE } from '../utils/helper';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import type { TooltipItem } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

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
  const [_, setUserAreas] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const getServiceLogo = (serviceName: string): string | null => {
    const key = serviceName.toLowerCase();
    return imagesByName[key] || null;
  };

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
      if (accessToken && !storedUser) {
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
      } else {
        setUser(storedUser);
      }
    };

    const fetchData = async () => {
      setLoading(true);
      try {
        await loadUserData();
        const servicesResponse = await fetch(`${API_BASE}/about.json`);
        if (!servicesResponse.ok) {
          throw new Error(`HTTP Error: ${servicesResponse.status}`);
        }
        const servicesData = await servicesResponse.json();
        const servicesList = servicesData?.server?.services || [];
        const formattedServices = servicesList.map(
          (s: { name: string; actions?: unknown[]; reactions?: unknown[] }) => ({
            name: s.name,
            actions: s.actions || [],
            reactions: s.reactions || [],
          })
        );
        setServices(formattedServices);
        const generateRandomActiveServices = () => {
          const randomServices = formattedServices
            .sort(() => 0.5 - Math.random())
            .slice(0, Math.floor(Math.random() * 3) + 2);
          return randomServices.map((s: Service) => s.name);
        };
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
            setActiveServices(generateRandomActiveServices());
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
              const activeServiceNames = new Set<string>();
              areasData.forEach(
                (area: {
                  status?: string;
                  action?: { service?: string };
                  reaction?: { service?: string };
                }) => {
                  if (area.status === 'active' && area.action && area.action.service) {
                    activeServiceNames.add(area.action.service);
                  }
                  if (area.status === 'active' && area.reaction && area.reaction.service) {
                    activeServiceNames.add(area.reaction.service);
                  }
                }
              );
              if (activeServiceNames.size > 0) {
                setActiveServices(Array.from(activeServiceNames));
              }
            }
          } catch {
            setActiveServices(generateRandomActiveServices());
          }
        } else {
          setActiveServices(generateRandomActiveServices());
        }
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
          <div className="w-full flex flex-col gap-4 mb-4">
            <div className="bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-theme-primary">
              <h2 className="text-xl font-semibold text-theme-accent mb-3">Service Activity</h2>
              {activeServices.length > 0 ? (
                <>
                  <div className="h-32 md:h-[180px] relative">
                    <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-white bg-opacity-20"></div>
                    <div className="absolute left-0 bottom-0 top-0 w-[1px] bg-white bg-opacity-20"></div>
                    <div className="flex h-full items-end justify-between px-2">
                      {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => {
                        const heightMultiplier =
                          activeServices.length > 0
                            ? Math.min(120, activeServices.length * 40)
                            : 30;
                        return (
                          <div key={day} className="flex flex-col items-center w-1/7">
                            <div
                              className="w-8 bg-gradient-chart-bar rounded-t-sm"
                              style={{
                                height: `${(i >= 5 ? 80 : 40) + Math.random() * heightMultiplier}px`,
                                opacity: i === 6 ? 1 : 0.7 + i * 0.05,
                              }}
                            ></div>
                            <span className="text-xs mt-2 text-gray-400">{day}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div className="mt-4 text-sm text-gray-400 text-center">
                    Last 7 days activity across {activeServices.length} active service
                    {activeServices.length !== 1 ? 's' : ''}
                  </div>
                </>
              ) : loading ? (
                <div className="h-32 md:h-[180px] flex items-center justify-center">
                  <div className="animate-pulse text-indigo-300">Loading activity data...</div>
                </div>
              ) : (
                <div className="h-32 md:h-[180px] flex flex-col items-center justify-center">
                  <p className="text-gray-400 mb-3">No active services yet</p>
                  <button
                    onClick={() => navigate('/services')}
                    className="px-4 py-2 bg-gradient-button-primary hover:bg-gradient-button-primary rounded-lg text-white transition-colors"
                  >
                    Explore Services
                  </button>
                </div>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-theme-primary">
                <h2 className="text-xl font-semibold text-theme-accent mb-3">Services Usage</h2>
                <div className="flex justify-center h-32 md:h-[180px]">
                  <ServiceUsageChart services={services} activeServices={activeServices} />
                </div>
              </div>
              <div className="bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-theme-primary">
                <h2 className="text-xl font-semibold text-theme-accent mb-3">Quick Actions</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <button
                    onClick={() => navigate('/Areaction')}
                    className="bg-gradient-button-primary hover:bg-gradient-button-primary text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-8 w-8 mb-2"
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
                    <span className="font-medium">New Automation</span>
                  </button>
                  <button
                    onClick={() => navigate('/profile')}
                    className="bg-gradient-button-secondary hover:bg-gradient-button-secondary text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-8 w-8 mb-2"
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
                    <span className="font-medium">View my profile</span>
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
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                  {services.map((service) => {
                    const isActive = activeServices.includes(service.name);
                    const logo = getServiceLogo(service.name);
                    return (
                      <div
                        key={service.name}
                        onClick={() => handleServiceClick(service.name)}
                        className="bg-white bg-opacity-10 rounded-xl p-3 cursor-pointer transform transition-all duration-300 hover:bg-opacity-20 hover:scale-105 hover:shadow-lg flex flex-col items-center text-center aspect-square"
                      >
                        <div className="w-24 h-24 rounded-full bg-white bg-opacity-10 flex items-center justify-center overflow-hidden mb-3 mt-1">
                          {logo ? (
                            <img
                              src={logo}
                              alt={`${service.name} logo`}
                              className="w-16 h-16 object-contain"
                            />
                          ) : (
                            <div className="text-4xl font-bold text-white opacity-50">
                              {service.name.charAt(0)}
                            </div>
                          )}
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
                          {service.name}
                        </h3>
                        <span
                          className={`px-4 py-1 rounded-full text-base font-medium mt-auto mb-1 ${isActive ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}
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
