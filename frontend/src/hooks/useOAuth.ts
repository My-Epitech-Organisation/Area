import { useState, useEffect, useCallback } from 'react';
import type { 
  ConnectedServicesResponse, 
  OAuthInitiateResponse,
  ServiceConnection 
} from '../types/api';

const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:8080';

/**
 * Hook to manage OAuth2 service connections
 */
export const useConnectedServices = () => {
  const [services, setServices] = useState<ServiceConnection[]>([]);
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchServices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('access');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${API_BASE}/auth/services/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch services: ${response.statusText}`);
      }

      const data: ConnectedServicesResponse = await response.json();
      setServices(data.connected_services);
      setAvailableProviders(data.available_providers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  return {
    services,
    availableProviders,
    loading,
    error,
    refetch: fetchServices,
  };
};

/**
 * Hook to initiate OAuth2 flow
 */
export const useInitiateOAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initiateOAuth = async (provider: string): Promise<OAuthInitiateResponse | null> => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('access');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${API_BASE}/auth/oauth/${provider}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Failed to initiate OAuth: ${response.statusText}`);
      }

      const data: OAuthInitiateResponse = await response.json();
      
      // Redirect to OAuth provider
      window.location.href = data.redirect_url;
      
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    initiateOAuth,
    loading,
    error,
  };
};

/**
 * Hook to disconnect a service
 */
export const useDisconnectService = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const disconnectService = async (provider: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('access');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${API_BASE}/auth/services/${provider}/disconnect/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Failed to disconnect service: ${response.statusText}`);
      }

      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    disconnectService,
    loading,
    error,
  };
};

/**
 * Utility hook to check if a service is connected
 */
export const useIsServiceConnected = (serviceName: string): boolean => {
  const { services, loading } = useConnectedServices();
  
  if (loading) return false;
  
  return services.some(
    service => service.service_name.toLowerCase() === serviceName.toLowerCase() && !service.is_expired
  );
};
