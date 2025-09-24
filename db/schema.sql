-- Enhanced Schema for AREA Platform (PostgreSQL)
-- command : psql -U myuser -d area_db -f db/script1.sql

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enums
CREATE TYPE auth_type AS ENUM('none','api_key','basic','oauth2');
CREATE TYPE service_status AS ENUM('active','inactive');
CREATE TYPE area_status AS ENUM('active','disabled','paused');
CREATE TYPE execution_status AS ENUM('success','failure','timeout','cancelled');
CREATE TYPE http_method AS ENUM('GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS');
CREATE TYPE param_type AS ENUM('string','number','boolean','json','array');
CREATE TYPE quota_period AS ENUM('day','month');
CREATE TYPE audit_operation AS ENUM('CREATE','READ','UPDATE','DELETE');

-- Core tables
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_login_at TIMESTAMPTZ
);

CREATE TABLE user_roles (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(user_id, role_id)
);

-- Services
CREATE TABLE services (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  endpoint TEXT NOT NULL,
  auth_type auth_type NOT NULL DEFAULT 'none',
  auth_config JSONB,
  status service_status NOT NULL DEFAULT 'active',
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Parameters
CREATE TABLE parameters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  type param_type NOT NULL DEFAULT 'string',
  required BOOLEAN NOT NULL DEFAULT false,
  description TEXT,
  default_value JSONB
);

-- Actions & Reactions
CREATE TABLE actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  params_schema JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(service_id,name)
);

CREATE TABLE reactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  params_schema JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(service_id,name)
);

-- Link to parameters
CREATE TABLE action_parameters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  action_id UUID NOT NULL REFERENCES actions(id) ON DELETE CASCADE,
  parameter_id UUID NOT NULL REFERENCES parameters(id) ON DELETE RESTRICT,
  position INT NOT NULL DEFAULT 0,
  default_value JSONB,
  required BOOLEAN NOT NULL DEFAULT false,
  UNIQUE(action_id,position),
  UNIQUE(action_id,parameter_id)
);
CREATE INDEX idx_action_params_json ON action_parameters USING GIN(default_value);

CREATE TABLE reaction_parameters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reaction_id UUID NOT NULL REFERENCES reactions(id) ON DELETE CASCADE,
  parameter_id UUID NOT NULL REFERENCES parameters(id) ON DELETE RESTRICT,
  position INT NOT NULL DEFAULT 0,
  default_value JSONB,
  required BOOLEAN NOT NULL DEFAULT false,
  UNIQUE(reaction_id,position),
  UNIQUE(reaction_id,parameter_id)
);
CREATE INDEX idx_reaction_params_json ON reaction_parameters USING GIN(default_value);

-- AREA mappings
CREATE TABLE areas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  action_id UUID NOT NULL REFERENCES actions(id) ON DELETE CASCADE,
  reaction_id UUID NOT NULL REFERENCES reactions(id) ON DELETE CASCADE,
  configuration JSONB NOT NULL,
  status area_status NOT NULL DEFAULT 'active',
  frequency TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Multi-step workflows
CREATE TABLE area_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  area_id UUID NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
  step_order INT NOT NULL,
  action_id UUID REFERENCES actions(id) ON DELETE CASCADE,
  reaction_id UUID REFERENCES reactions(id) ON DELETE CASCADE,
  config JSONB,
  UNIQUE(area_id,step_order)
);

-- Scheduling
CREATE TABLE schedules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  area_id UUID NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
  cron_expression TEXT NOT NULL,
  timezone TEXT NOT NULL DEFAULT 'UTC',
  enabled BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Webhooks
CREATE TABLE webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  area_id UUID NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  method http_method NOT NULL DEFAULT 'POST',
  secret BYTEA,
  enabled BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Templates
CREATE TABLE templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  configuration JSONB NOT NULL,
  is_public BOOLEAN NOT NULL DEFAULT false,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE template_users (
  template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  custom_configuration JSONB,
  saved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(template_id,user_id)
);

-- Execution logs (no partitioning to avoid PK issues)
CREATE TABLE execution_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  area_id UUID NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status execution_status NOT NULL,
  duration_ms INT,
  payload_input JSONB,
  payload_output JSONB,
  error_message TEXT,
  details JSONB
);
CREATE INDEX idx_exec_logs_recent ON execution_logs(area_id,occurred_at DESC);
CREATE INDEX idx_exec_logs_payload ON execution_logs USING GIN(payload_input);

-- Quotas & Usage
CREATE TABLE quotas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  period quota_period NOT NULL,
  max_executions INT NOT NULL CHECK (max_executions >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(user_id,period)
);

CREATE TABLE usage_counters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  period quota_period NOT NULL,
  executions INT NOT NULL DEFAULT 0 CHECK (executions >= 0),
  UNIQUE(user_id,period_start,period),
  CHECK (period_end > period_start)
);

-- Audit trail (no partitioning)
CREATE TABLE audit_trail (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  entity_table TEXT NOT NULL,
  entity_id UUID,
  operation audit_operation NOT NULL,
  changed_data JSONB,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ip_address INET,
  user_agent TEXT
);
CREATE INDEX idx_audit_time ON audit_trail(occurred_at);
CREATE INDEX idx_audit_entity ON audit_trail(entity_table);

-- Seed roles
INSERT INTO roles(name) VALUES('admin'),('user'),('manager')
  ON CONFLICT DO NOTHING;

