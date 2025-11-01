import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useConnectedServices, useInitiateOAuth, useDisconnectService } from '../hooks/useOAuth';
import { useNotifications } from '../hooks/useNotifications';
import { useAuthCheck } from '../hooks/useAuthCheck';
import Notification from '../components/Notification';
import GitHubAppSection from '../components/GitHubAppSection';
import NotionWebhookSection from '../components/NotionWebhookSection';
import { API_BASE, getStoredUser } from '../utils/helper';
import type { User } from '../types';

type ServiceAction = {
  name: string;
  description: string;
};

type ServiceReaction = {
  name: string;
  description: string;
};

type Service = {
  name: string;
  logo: string;
  actions: ServiceAction[];
  reactions: ServiceReaction[];
};

const ServiceDetail: React.FC = () => {
  const { serviceId } = useParams<{ serviceId: string }>();
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [notionPageId, setNotionPageId] = useState<string | undefined>(undefined);
  const [notionDatabaseId, setNotionDatabaseId] = useState<string | undefined>(undefined);

  // Verify authentication status on page load
  useAuthCheck();

  const isInternalService = (serviceName: string) => {
    return ['timer', 'debug', 'email', 'webhook', 'weather'].includes(serviceName.toLowerCase());
  };

  // Load user data
  useEffect(() => {
    const storedUser = getStoredUser();
    if (storedUser) {
      setUser(storedUser);
    }
  }, []);

  // Fetch user's Notion Areas to extract page_id/database_id for webhook configuration
  useEffect(() => {
    const fetchNotionConfig = async () => {
      if (!user || service?.name.toLowerCase() !== 'notion') return;

      try {
        const token = localStorage.getItem('access');
        if (!token) return;

        const response = await fetch(`${API_BASE}/api/areas/`, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const areas = await response.json();

          // Extract page_id and database_id from Notion Areas
          for (const area of areas) {
            if (area.action_config?.page_id) {
              setNotionPageId(area.action_config.page_id);
            }
            if (area.action_config?.database_id) {
              setNotionDatabaseId(area.action_config.database_id);
              break; // Use first found database_id
            }
          }
        }
      } catch (err) {
        console.error('Failed to fetch Notion configuration:', err);
      }
    };

    fetchNotionConfig();
  }, [user, service]);

  // OAuth hooks
  const {
    services: connectedServices,
    loading: loadingOAuth,
    refetch: refetchServices,
  } = useConnectedServices();
  const { initiateOAuth, loading: connectingOAuth } = useInitiateOAuth();
  const { disconnectService, loading: disconnectingOAuth } = useDisconnectService();

  // Notifications
  const { notifications, removeNotification, success, error: showError } = useNotifications();

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

  const resolveLogo = (rawLogo: string | null, name: string): string | null => {
    if (rawLogo) {
      if (/^(https?:)?\/\//.test(rawLogo) || rawLogo.startsWith('/')) {
        return rawLogo;
      }
      const base =
        rawLogo
          .split('/')
          .pop()
          ?.replace(/\.[^/.]+$/, '')
          .toLowerCase() ?? '';
      if (imagesByName[base]) return imagesByName[base];
    }

    const key = name.toLowerCase();
    return imagesByName[key] ?? null;
  };

  useEffect(() => {
    const fetchServiceDetails = async () => {
      setLoading(true);
      try {
        const baseUrl = API_BASE.replace(/\/api$/, '');
        const res = await fetch(`${baseUrl}/about.json`);
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        const serviceList = data?.server?.services || [];
        const foundService = serviceList.find(
          (s: { id?: string | number; name?: string }) =>
            s.id?.toString() === serviceId || s.name?.toLowerCase() === serviceId?.toLowerCase()
        );
        if (foundService) {
          setService(foundService);
          setError(null);
        } else {
          setError('Service not found');
        }
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : 'Failed to load service details');
      } finally {
        setLoading(false);
      }
    };
    fetchServiceDetails();
  }, [serviceId]);

  if (loading) {
    return (
      <div className="w-screen min-h-screen bg-page-about flex flex-col items-center justify-center p-6">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500"></div>
        <p className="text-white mt-4">Loading service details...</p>
      </div>
    );
  }

  if (error || !service) {
    return (
      <div className="w-screen min-h-screen bg-page-about flex flex-col items-center justify-center p-6">
        <div className="max-w-2xl w-full bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
          <h2 className="text-2xl font-bold text-theme-primary mb-4">Error</h2>
          <p className="text-theme-error">{error || 'Service not found'}</p>
          <Link
            to="/services"
            className="mt-6 inline-block px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
          >
            Back to Services
          </Link>
        </div>
      </div>
    );
  }

  const logo = resolveLogo(service.logo, service.name);

  // Check if this service requires OAuth and if it's connected
  // Google Calendar and Gmail use the same OAuth as Google
  const oauthProviders = [
    'github',
    'google',
    'gmail',
    'google_calendar',
    'twitch',
    'slack',
    'spotify',
    'notion',
  ];
  const requiresOAuth = service && oauthProviders.includes(service.name.toLowerCase());

  // For gmail and google_calendar, check if 'google' OAuth is connected
  const getOAuthServiceName = (serviceName: string) => {
    const lower = serviceName.toLowerCase();
    if (lower === 'gmail' || lower === 'google_calendar') {
      return 'google';
    }
    return lower;
  };

  const oauthServiceName = getOAuthServiceName(service.name);

  const isConnected =
    requiresOAuth &&
    connectedServices.some((s) => {
      const match = s.service_name.toLowerCase() === oauthServiceName && !s.is_expired;
      return match;
    });

  const handleConnect = async () => {
    if (service) {
      await initiateOAuth(oauthServiceName);
    }
  };

  const handleDisconnect = async () => {
    if (service && window.confirm(`Are you sure you want to disconnect ${service.name}?`)) {
      try {
        const result = await disconnectService(oauthServiceName);
        if (result) {
          success(`${service.name} has been disconnected successfully!`);
          // Refresh the connected services list without reloading the page
          await refetchServices();
        } else {
          showError(`Failed to disconnect ${service.name}. Please try again.`);
        }
      } catch (err) {
        showError(`An error occurred while disconnecting ${service.name}, error: ${err}`);
      }
    }
  };

  return (
    <div className="w-screen min-h-screen bg-page-service-detail p-6">
      {/* Notifications */}
      {notifications.map((notification) => (
        <Notification
          key={notification.id}
          type={notification.type}
          message={notification.message}
          onClose={() => removeNotification(notification.id)}
        />
      ))}

      <div className="max-w-6xl mx-auto pt-20">
        <Link
          to="/services"
          className="text-theme-accent hover:text-theme-secondary flex items-center gap-2 mb-8 transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
          Back to services
        </Link>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 shadow-xl">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            <div className="w-32 h-32 bg-white/10 rounded-xl flex items-center justify-center overflow-hidden p-2">
              {logo ? (
                <img
                  src={logo}
                  alt={`${service.name} logo`}
                  className="w-full h-full object-contain"
                  style={
                    isInternalService(service.name)
                      ? {
                          filter:
                            'drop-shadow(0 0 1px rgba(255,255,255,0.6)) drop-shadow(0 0 2px rgba(255,255,255,0.4))',
                        }
                      : undefined
                  }
                />
              ) : (
                <span className="text-4xl font-bold text-white">
                  {service.name.charAt(0).toUpperCase()}
                </span>
              )}
            </div>

            <div className="flex-1">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <h1 className="text-3xl md:text-4xl font-bold text-white text-center md:text-left">
                  {service.name.charAt(0).toUpperCase() + service.name.slice(1)}
                </h1>

                {/* OAuth Connection Status */}
                {requiresOAuth && (
                  <div className="flex items-center gap-3">
                    {isConnected ? (
                      <>
                        <div className="flex items-center gap-2 bg-green-500/20 text-green-300 px-4 py-2 rounded-lg border border-green-500/30">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path
                              fillRule="evenodd"
                              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="font-medium">Connected</span>
                        </div>
                        <button
                          onClick={handleDisconnect}
                          disabled={disconnectingOAuth}
                          className="px-4 py-2 text-sm bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/30 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Disconnect
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={handleConnect}
                        disabled={connectingOAuth || loadingOAuth}
                        className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {connectingOAuth ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                            <span>Connecting...</span>
                          </>
                        ) : (
                          <>
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-5 w-5"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path
                                fillRule="evenodd"
                                d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"
                                clipRule="evenodd"
                              />
                            </svg>
                            <span>Connect {service.name}</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* GitHub App Section - Show only for GitHub service */}
              {service.name.toLowerCase() === 'github' && (
                <GitHubAppSection user={user} isOAuthConnected={isConnected} />
              )}

              {/* Notion Webhook Section - Show only for Notion service */}
              {service.name.toLowerCase() === 'notion' && (
                <NotionWebhookSection
                  user={user}
                  isOAuthConnected={isConnected}
                  pageId={notionPageId}
                  databaseId={notionDatabaseId}
                />
              )}

              <div className="mt-8 grid gap-8 md:grid-cols-2">
                <div>
                  <h2 className="text-xl font-semibold text-indigo-300 mb-4 flex items-center gap-2">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                    Actions
                  </h2>
                  {service.actions && service.actions.length > 0 ? (
                    <div className="space-y-3">
                      {service.actions.map((action, index) => (
                        <div
                          key={`action-${index}`}
                          className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition"
                        >
                          <h3 className="font-medium text-white">
                            {action.name
                              .split('_')
                              .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                              .join(' ')}
                          </h3>
                          <p className="text-sm text-gray-300 mt-1">{action.description}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No actions available</p>
                  )}
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-indigo-300 mb-4 flex items-center gap-2">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    Reactions
                  </h2>
                  {service.reactions && service.reactions.length > 0 ? (
                    <div className="space-y-3">
                      {service.reactions.map((reaction, index) => (
                        <div
                          key={`reaction-${index}`}
                          className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition"
                        >
                          <h3 className="font-medium text-white">
                            {reaction.name
                              .split('_')
                              .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                              .join(' ')}
                          </h3>
                          <p className="text-sm text-gray-300 mt-1">{reaction.description}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No reactions available</p>
                  )}
                </div>
              </div>

              <div className="mt-10 flex justify-center md:justify-start">
                <Link
                  to={`/Areaction?service=${service.name}${service.actions && service.actions.length > 0 ? `&action=${service.actions[0].name}` : ''}${service.reactions && service.reactions.length > 0 ? `&reaction=${service.reactions[0].name}` : ''}`}
                  className="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium flex items-center gap-2 transition-colors"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Add Automation with this Service
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceDetail;
