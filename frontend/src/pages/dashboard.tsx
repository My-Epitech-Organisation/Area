/*
** EPITECH PROJECT, 2025
** Area
** File description:
** dashboard
*/

import React, {useState, useEffect} from "react";
import { useNavigate } from "react-router-dom";
import type { Service, User } from "../types";
import { getStoredUser, getAccessToken } from "../utils/helper";

const API_BASE = (import.meta.env.VITE_API_BASE as string) || "http://localhost:8080";

const imageModules = import.meta.glob("../assets/*.{png,jpg,jpeg,svg,gif}", { eager: true }) as Record<string, { default: string }>;
const imagesByName: Record<string, string> = {};

Object.keys(imageModules).forEach((p) => {
  const parts = p.split("/");
  const file = parts[parts.length - 1];
  const name = file.replace(/\.[^/.]+$/, "").toLowerCase();
  imagesByName[name] = (imageModules as any)[p].default;
});

const originalFetch = window.fetch;
window.fetch = async function(input: RequestInfo | URL, init?: RequestInit) {
  try {
    const response = await originalFetch(input, init);
    return response;
  } catch (error) {
    throw error;
  }
};

const Dashboard: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [activeServices, setActiveServices] = useState<string[]>([]);
  const [userAreas, setUserAreas] = useState<any[]>([]);
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
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key) {
        const value = localStorage.getItem(key);
      }
    }
    const storedUser = getStoredUser();
    const accessToken = getAccessToken();
    const storedUsername = localStorage.getItem('username');
    const storedEmail = localStorage.getItem('email');

    if (accessToken && !storedUser) {
      const tempUser = {
        name: storedUsername || storedEmail || "User",
        username: storedUsername || "User",
        email: storedEmail || "user@example.com",
        id: "temp"
      };
      setUser(tempUser);
    }

    const extractUserFromToken = (token: string): any => {
      try {
        const base64Url = token.split('.')[1];
        if (!base64Url)
          return null;

        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
          atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
          }).join('')
        );

        return JSON.parse(jsonPayload);
      } catch (e) {
        console.error("Error parsing JWT token:", e);
        return null;
      }
    };

    const fetchUserData = async () => {
      if (accessToken && !storedUser) {
        try {
          const userResponse = await fetch(`${API_BASE}/auth/me/`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });
          if (userResponse.ok) {
            const userData = await userResponse.json();
            const userToStore = {
              name: userData.username || userData.email || "User",
              username: userData.username || "User",
              email: userData.email,
              id: userData.id || userData.pk
            };
            localStorage.setItem('user', JSON.stringify(userToStore));
            setUser(userToStore);
          } else {
            const errorData = await userResponse.text();
            console.error("API error:", errorData);
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
                    console.error("Error extracting data from refresh token:", e);
                  }
                }
                try {
                  const userDetailResponse = await fetch(`${API_BASE}/auth/me/`, {
                    headers: {
                      'Authorization': `Bearer ${accessToken}`
                    }
                  });
                  if (userDetailResponse.ok) {
                    const userDetailData = await userDetailResponse.json();
                    const userFromDetail = {
                      name: userDetailData.username || userDetailData.email || username || `User ${userId.substring(0, 6)}`,
                      username: userDetailData.username || username || `User ${userId.substring(0, 6)}`,
                      email: userDetailData.email,
                      id: userId
                    };
                    localStorage.setItem('user', JSON.stringify(userFromDetail));
                    setUser(userFromDetail);
                  } else {
                    const displayName = username || `User ${userId.substring(0, 6)}`;
                    const userFromToken = {
                      name: displayName,
                      username: displayName,
                      id: userId
                    };
                    localStorage.setItem('user', JSON.stringify(userFromToken));
                    setUser(userFromToken);
                  }
                } catch (error) {
                  console.error("Failed to fetch user details:", error);
                  const displayName = username || `User ${userId.substring(0, 6)}`;
                  const userFromToken = {
                    name: displayName,
                    username: displayName,
                    id: userId
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
                  console.error("Error extracting data from refresh token (fallback):", e);
                }
              }
              const displayName = username || `User ${userId.substring(0, 6)}`;
              const userFromToken = {
                name: displayName,
                username: displayName,
                id: userId
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
        await fetchUserData();
        const servicesResponse = await fetch(`${API_BASE}/about.json`);
        if (!servicesResponse.ok) {
          throw new Error(`HTTP Error: ${servicesResponse.status}`);
        }
        const servicesData = await servicesResponse.json();
        const servicesList = servicesData?.server?.services || [];
        const formattedServices = servicesList.map((s: any) => ({
          name: s.name,
          actions: s.actions || [],
          reactions: s.reactions || []
        }));
        setServices(formattedServices);
        const generateRandomActiveServices = () => {
          const randomServices = formattedServices
            .sort(() => 0.5 - Math.random())
            .slice(0, Math.floor(Math.random() * 3) + 2);
          return randomServices.map((s: Service) => s.name);
        };
        const isFullyAuthenticated = () => {
          return storedUser &&
                 accessToken &&
                 storedUser.id &&
                 (storedUser.username || storedUser.name || storedUser.email);
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
                  'Authorization': `Bearer ${accessToken}`,
                  'Content-Type': 'application/json'
                }
              },
              5000
            ).catch(error => {
              if (error.name === 'AbortError') {
                console.error("Areas fetch timed out");
              } else {
                console.error("Areas fetch failed:", error.message);
              }
              return null;
            });

            if (areasResponse && areasResponse.ok) {
              const areasData = await areasResponse.json();
              setUserAreas(areasData);
              const activeServiceNames = new Set<string>();
              areasData.forEach((area: any) => {
                if (area.status === 'active' && area.action && area.action.service) {
                  activeServiceNames.add(area.action.service);
                }
                if (area.status === 'active' && area.reaction && area.reaction.service) {
                  activeServiceNames.add(area.reaction.service);
                }
              });
              if (activeServiceNames.size > 0) {
                setActiveServices(Array.from(activeServiceNames));
              }
            }
          } catch (areaErr) {
            setActiveServices(generateRandomActiveServices());
          }
        } else {
          setActiveServices(generateRandomActiveServices());
        }
        setError(null);
      } catch (err: any) {
        console.error("Failed to fetch services:", err);
        setError(err.message || "Failed to load services");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="w-full min-h-screen bg-dashboard flex pt-16">
      <div className="flex flex-1 h-screen">
        <div className="flex-1 p-8 flex flex-col items-center">
          <header className="w-full flex flex-col items-center pt-6 mb-6">
            <h1 className="text-5xl font-bold text-center text-white mb-3">Dashboard</h1>
            <div className="w-full flex items-center justify-center">
              {user ? (
                <p className="text-3xl font-semibold text-indigo-300 mt-2 animate-fadeIn">
                  Welcome back, {user.username || user.name}!
                </p>
              ) : (
                <p className="text-2xl font-semibold text-amber-400 mt-2 animate-pulse">
                  <span onClick={() => navigate('/login')} className="cursor-pointer hover:underline">
                    Sign in to unlock all features
                  </span>
                </p>
              )}
            </div>
          </header>
          <div className="w-full grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-gray-200">
              <h2 className="text-xl font-semibold text-indigo-300 mb-4">Service Activity</h2>
              {activeServices.length > 0 ? (
                <>
                  <div className="h-[200px] relative">
                    <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-white bg-opacity-20"></div>
                    <div className="absolute left-0 bottom-0 top-0 w-[1px] bg-white bg-opacity-20"></div>
                    <div className="flex h-full items-end justify-between px-2">
                      {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => {
                        const heightMultiplier = activeServices.length > 0 ?
                          Math.min(120, activeServices.length * 40) : 30;
                        return (
                          <div key={day} className="flex flex-col items-center w-1/7">
                            <div
                              className="w-8 bg-gradient-to-t from-indigo-600 to-indigo-400 rounded-t-sm"
                              style={{
                                height: `${(i >= 5 ? 80 : 40) + (Math.random() * heightMultiplier)}px`,
                                opacity: i === 6 ? 1 : 0.7 + (i * 0.05)
                              }}
                            ></div>
                            <span className="text-xs mt-2 text-gray-400">{day}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div className="mt-4 text-sm text-gray-400 text-center">
                    Last 7 days activity across {activeServices.length} active service{activeServices.length !== 1 ? 's' : ''}
                  </div>
                </>
              ) : loading ? (
                <div className="h-[200px] flex items-center justify-center">
                  <div className="animate-pulse text-indigo-300">Loading activity data...</div>
                </div>
              ) : (
                <div className="h-[200px] flex flex-col items-center justify-center">
                  <p className="text-gray-400 mb-3">No active services yet</p>
                  <button
                    onClick={() => navigate('/services')}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-white transition-colors"
                  >
                    Explore Services
                  </button>
                </div>
              )}
            </div>
            <div className="bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-gray-200">
              <h2 className="text-xl font-semibold text-indigo-300 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => navigate('/services')}
                  className="bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span className="font-medium">New Automation</span>
                </button>
                <button
                  onClick={() => navigate('/services')}
                  className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span className="font-medium">Connect Service</span>
                </button>
                <button
                  onClick={() => navigate('/templates')}
                  className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2a1 1 0 001 1h14a1 1 0 001-1v-2c0-2.66-5.33-4-8-4z" />
                  </svg>
                  <span className="font-medium">View my profile</span>
                </button>
                <button
                  onClick={() => navigate('/areas')}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-xl p-4 flex flex-col items-center justify-center transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <span className="font-medium">My Automations</span>
                </button>
              </div>
            </div>
            <div className="lg:col-span-2 bg-white bg-opacity-10 border border-white border-opacity-10 rounded-2xl p-5 text-gray-200">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-indigo-300">Recent Notifications</h2>
                <button className="text-xs text-indigo-300 hover:text-indigo-200 transition-colors">Mark all as read</button>
              </div>
              <div className="space-y-3">
                <div className="flex items-start p-3 bg-white bg-opacity-5 rounded-lg hover:bg-opacity-10 transition-all cursor-pointer">
                  <div className="rounded-full bg-amber-500 p-2 mr-3">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Your "Daily Weather Report" automation failed</p>
                    <p className="text-xs text-gray-400 mt-1">Gmail service authentication expired</p>
                  </div>
                  <div className="text-xs text-gray-500">2h ago</div>
                </div>
                <div className="flex items-start p-3 bg-white bg-opacity-5 rounded-lg hover:bg-opacity-10 transition-all cursor-pointer">
                  <div className="rounded-full bg-green-500 p-2 mr-3">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Successfully connected to Github service</p>
                    <p className="text-xs text-gray-400 mt-1">You can now create automations with Github</p>
                  </div>
                  <div className="text-xs text-gray-500">5h ago</div>
                </div>
                <div className="flex items-start p-3 bg-white bg-opacity-5 rounded-lg hover:bg-opacity-10 transition-all cursor-pointer">
                  <div className="rounded-full bg-blue-500 p-2 mr-3">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">New service available: Slack</p>
                    <p className="text-xs text-gray-400 mt-1">Connect Slack to create automations with your workspace</p>
                  </div>
                  <div className="text-xs text-gray-500">1d ago</div>
                </div>
              </div>
              <div className="mt-4 text-center">
                <button className="text-sm text-indigo-300 hover:text-indigo-200 transition-colors">
                  View all notifications
                </button>
              </div>
            </div>
          </div>
        </div>
        <aside className="w-[450px] h-full bg-black bg-opacity-20 border-l border-white border-opacity-10 overflow-y-auto p-5 pt-3">
          <h2 className="text-2xl font-bold text-indigo-400 mb-4 text-center">Services</h2>
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
            <div className="grid grid-cols-3 gap-3">
              {services.map((service) => {
                const isActive = activeServices.includes(service.name);
                const logo = getServiceLogo(service.name);
                return (
                  <div
                    key={service.name}
                    onClick={() => handleServiceClick(service.name)}
                    className="bg-white bg-opacity-10 rounded-xl p-3 cursor-pointer transform transition-all duration-300 hover:bg-opacity-20 hover:scale-105 hover:shadow-lg flex flex-col items-center text-center aspect-square"
                  >
                    <div className="w-14 h-14 rounded-full bg-white bg-opacity-10 flex items-center justify-center overflow-hidden mb-3 mt-1">
                      {logo ? (
                        <img
                          src={logo}
                          alt={`${service.name} logo`}
                          className="w-10 h-10 object-contain"
                        />
                      ) : (
                        <div className="text-2xl font-bold text-white opacity-50">
                          {service.name.charAt(0)}
                        </div>
                      )}
                    </div>
                    <h3 className="text-sm font-semibold text-white mb-2 line-clamp-2">
                      {service.name}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium mt-auto mb-1 ${isActive ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}>
                      {isActive ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;
