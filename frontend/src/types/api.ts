/**
 * Type definitions for AREA API responses
 */

// JSON Schema types for dynamic form generation
export interface JSONSchemaProperty {
  type: 'string' | 'number' | 'integer' | 'boolean' | 'array' | 'object';
  description?: string;
  format?: string;
  pattern?: string;
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
  enum?: any[];
  default?: any;
  items?: JSONSchemaProperty;
  properties?: Record<string, JSONSchemaProperty>;
  additionalProperties?: boolean | JSONSchemaProperty;
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
