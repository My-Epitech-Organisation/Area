/**
 * Type definitions for AREA API responses
 */

// JSON Schema types for dynamic form generation
export interface JSONSchemaProperty {
  type: 'string' | 'number' | 'integer' | 'boolean' | 'array' | 'object' | 'text' | 'datetime';
  description?: string;
  label?: string;
  placeholder?: string;
  format?: string;
  pattern?: string;
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
  enum?: (string | number | boolean)[];
  default?: string | number | boolean | null;
  items?: JSONSchemaProperty;
  properties?: Record<string, JSONSchemaProperty>;
  additionalProperties?: boolean | JSONSchemaProperty;
  min?: number;
  max?: number;
}

export interface JSONSchema {
  type: 'object';
  properties: Record<string, JSONSchemaProperty>;
  required?: string[];
  additionalProperties?: boolean;
}

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
  service_name?: string;
  config_schema?: JSONSchema;
}

export interface Reaction {
  id: number;
  service: number;
  name: string;
  description: string;
  service_name?: string;
  config_schema?: JSONSchema;
}

export interface Area {
  id: number;
  owner: number;
  name: string;
  action: number;
  reaction: number;
  action_config: Record<string, unknown>;
  reaction_config: Record<string, unknown>;
  status: 'active' | 'disabled' | 'paused';
  created_at: string;
}

export interface CreateAreaPayload {
  name: string;
  action: number;
  reaction: number;
  action_config?: Record<string, unknown>;
  reaction_config?: Record<string, unknown>;
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
  [key: string]: unknown;
}

// OAuth2 / Service Connection types
export interface ServiceConnection {
  service_name: string;
  created_at: string;
  expires_at: string | null;
  is_expired: boolean;
  expires_in_minutes: number | null;
  has_refresh_token: boolean;
}

export interface ConnectedServicesResponse {
  connected_services: ServiceConnection[];
  available_providers: string[];
  total_connected: number;
}

export interface OAuthInitiateResponse {
  redirect_url: string;
  state: string;
  provider: string;
  expires_in: number;
}

export interface OAuthCallbackResponse {
  message: string;
  service: string;
  created: boolean;
  expires_at?: string;
}
