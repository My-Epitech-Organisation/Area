-- seed.sql : jeu de données de démonstration pour AREA Platform

-- Organisations
INSERT INTO organizations (id, name, metadata)
VALUES
  (gen_random_uuid(), 'OrgA', '{"sector":"IT"}'),
  (gen_random_uuid(), 'OrgB', '{"sector":"Marketing"}')
ON CONFLICT DO NOTHING;

-- Rôles
INSERT INTO roles (name)
VALUES
  ('admin'),
  ('user'),
  ('manager')
ON CONFLICT DO NOTHING;

-- Utilisateurs
WITH org AS (
  SELECT id AS org_id FROM organizations WHERE name='OrgA'
)
INSERT INTO users (id, organization_id, email, password_hash, is_active)
VALUES
  (gen_random_uuid(), (SELECT org_id FROM org), 'alice@orga.com', crypt('alicepwd', gen_salt('bf')), TRUE),
  (gen_random_uuid(), (SELECT org_id FROM org), 'bob@orga.com',   crypt('bobpwd',   gen_salt('bf')), TRUE)
ON CONFLICT DO NOTHING;

-- Attribution de rôles
WITH u AS (SELECT id AS user_id FROM users WHERE email='alice@orga.com'),
     r AS (SELECT id AS role_id FROM roles   WHERE name='admin')
INSERT INTO user_roles (user_id, role_id)
VALUES ((SELECT user_id FROM u),(SELECT role_id FROM r))
ON CONFLICT DO NOTHING;

-- Services externes
INSERT INTO services (id, name, endpoint, auth_type, status)
VALUES
  (gen_random_uuid(), 'Gmail', 'https://api.gmail.com', 'oauth2', 'active'),
  (gen_random_uuid(), 'Slack', 'https://slack.com/api',  'api_key', 'active')
ON CONFLICT DO NOTHING;

-- Paramètres réutilisables
INSERT INTO parameters (id, name, type, required, description)
VALUES
  (gen_random_uuid(), 'to',      'string', TRUE,  'Adresse destinataire'),
  (gen_random_uuid(), 'subject', 'string', FALSE, 'Objet du message'),
  (gen_random_uuid(), 'channel', 'string', TRUE,  'Canal Slack')
ON CONFLICT DO NOTHING;

-- Actions
WITH s1 AS (SELECT id FROM services WHERE name='Gmail'),
     s2 AS (SELECT id FROM services WHERE name='Slack')
INSERT INTO actions (id, service_id, name, description)
VALUES
  (gen_random_uuid(), (SELECT id FROM s1), 'NewEmail',  'Déclenchement sur nouvel email'),
  (gen_random_uuid(), (SELECT id FROM s2), 'NewMessage','Déclenchement sur nouveau message')
ON CONFLICT DO NOTHING;

-- Réactions
WITH s1 AS (SELECT id FROM services WHERE name='Gmail'),
     s2 AS (SELECT id FROM services WHERE name='Slack')
INSERT INTO reactions (id, service_id, name, description)
VALUES
  (gen_random_uuid(), (SELECT id FROM s1), 'SendEmail',  'Envoyer un email'),
  (gen_random_uuid(), (SELECT id FROM s2), 'PostMessage','Poster un message Slack')
ON CONFLICT DO NOTHING;

-- Liaison Action → Paramètre
WITH a AS (SELECT id FROM actions WHERE name='NewEmail'),
     p1 AS (SELECT id FROM parameters WHERE name='to'),
     p2 AS (SELECT id FROM parameters WHERE name='subject')
INSERT INTO action_parameters (id, action_id, parameter_id, position, required)
VALUES
  (gen_random_uuid(), (SELECT id FROM a),(SELECT id FROM p1), 1, TRUE),
  (gen_random_uuid(), (SELECT id FROM a),(SELECT id FROM p2), 2, FALSE)
ON CONFLICT DO NOTHING;

-- Liaison Réaction → Paramètre
WITH r AS (SELECT id FROM reactions WHERE name='SendEmail'),
     p1 AS (SELECT id FROM parameters WHERE name='to'),
     p2 AS (SELECT id FROM parameters WHERE name='subject')
INSERT INTO reaction_parameters (id, reaction_id, parameter_id, position, required)
VALUES
  (gen_random_uuid(), (SELECT id FROM r),(SELECT id FROM p1), 1, TRUE),
  (gen_random_uuid(), (SELECT id FROM r),(SELECT id FROM p2), 2, FALSE)
ON CONFLICT DO NOTHING;

-- Enchaînements AREA
WITH u AS (SELECT id FROM users WHERE email='alice@orga.com'),
     a AS (SELECT id FROM actions WHERE name='NewEmail'),
     r AS (SELECT id FROM reactions WHERE name='SendEmail'),
     org AS (SELECT id FROM organizations WHERE name='OrgA')
INSERT INTO areas (id, user_id, organization_id, action_id, reaction_id, configuration, frequency)
VALUES
  (gen_random_uuid(), (SELECT id FROM u),(SELECT id FROM org),(SELECT id FROM a),(SELECT id FROM r),
   '{"mapping":{"to":"to","subject":"subject"}}', '*/5 * * * *')
ON CONFLICT DO NOTHING;

-- Planification
WITH ar AS (SELECT id FROM areas LIMIT 1)
INSERT INTO schedules (id, area_id, cron_expression)
VALUES
  (gen_random_uuid(), (SELECT id FROM ar), '*/5 * * * *')
ON CONFLICT DO NOTHING;

-- Webhooks
WITH ar AS (SELECT id FROM areas LIMIT 1)
INSERT INTO webhooks (id, area_id, url, method)
VALUES
  (gen_random_uuid(), (SELECT id FROM ar), 'https://myapp.local/webhook', 'POST')
ON CONFLICT DO NOTHING;

-- Quotas et usage
WITH u AS (SELECT id FROM users WHERE email='alice@orga.com')
INSERT INTO quotas (id, user_id, period, max_executions)
VALUES
  (gen_random_uuid(), (SELECT id FROM u), 'day',   100),
  (gen_random_uuid(), (SELECT id FROM u), 'month', 2000)
ON CONFLICT DO NOTHING;

WITH u AS (SELECT id FROM users WHERE email='alice@orga.com')
INSERT INTO usage_counters (id, user_id, period_start, period_end, period, executions)
VALUES
  (gen_random_uuid(), (SELECT id FROM u), CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 'day', 0)
ON CONFLICT DO NOTHING;
