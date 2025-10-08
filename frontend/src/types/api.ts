/**
 * Type definitions for AREA API responses
 */

export interface Service {
  id: number;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  logo?: string;
}

export interface Action {
  id: number;
  service: number;
  name: string;
  description: string;
}

export interface Reaction {
  id: number;
  service: number;
  name: string;
  description: string;
}

export interface Area {
  id: number;
  owner: number;
  name: string;
  action: number;
  reaction: number;
  action_config: Record<string, any>;
  reaction_config: Record<string, any>;
  status: 'active' | 'disabled' | 'paused';
  created_at: string;
}

export interface CreateAreaPayload {
  name: string;
  action: number;
  reaction: number;
  action_config?: Record<string, any>;
  reaction_config?: Record<string, any>;
  status?: 'active' | 'disabled' | 'paused';
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  [key: string]: any;
}
