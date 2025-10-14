export interface ServiceModel {
  id: string;
  name: string;
  description?: string;
  logo?: string;
  requiresOAuth?: boolean;
  oauthUrl?: string;
  status?: 'active' | 'inactive' | 'pending';
  actions?: ActionModel[];
  reactions?: ReactionModel[];
  color?: string;
  icon?: string;
  [key: string]: unknown;
}

export interface ActionModel {
  id: string;
  name: string;
  description?: string;
  service?: string;
  serviceId?: string;
  config?: ConfigFieldModel[];
  [key: string]: unknown;
}

export interface ReactionModel {
  id: string;
  name: string;
  description?: string;
  service?: string;
  serviceId?: string;
  config?: ConfigFieldModel[];
  [key: string]: unknown;
}

export interface ConfigFieldModel {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'datetime' | 'date' | 'time';
  label: string;
  required?: boolean;
  placeholder?: string;
  defaultValue?: string | number | boolean;
  options?: { label: string; value: string }[];
  [key: string]: unknown;
}

export interface ErrorResponse {
  message: string;
  fields?: Record<string, string[]>;
  [key: string]: unknown;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ErrorResponse;
  [key: string]: unknown;
}

export type ImageModule = Record<string, { default: string }>;

export interface KeyValuePair<T = unknown> {
  [key: string]: T;
}
