# PostgreSQL & Query Tool Guide

> **Prerequisite**: You can launch both PostgreSQL using Docker Compose. See `docker-compose.md` for setup instructions.

This document provides a concise reference for working with your **AREA** database schema in PostgreSQL, using both **psql** (CLI) and the **Query Tool**.

## 1. Connecting to the Database

### 1.1 Via Docker Compose

Ensure you have started the stack:

```bash
docker-compose up -d
```

This brings up:

- PostgreSQL on port **5432**

### 1.2 Via psql

```bash
psql -h localhost -U myuser -d area_db
```

- Enter **secret_password** when prompted.

## 2. Basic psql Commands

- **List all tables**:

  ```sql
  \dt public.*
  ```

- **Describe table structure**:

  ```sql
  \d table_name
  ```

- **Import SQL file**:

  ```sql
  \i path/to/schema.sql
  ```

- **Exit psql**:

  ```sql
  \q
  ```

## 3. Query Tool Workflow

1. **Open Query Tool**: In your SQL client, select the AreaDB connection and open the Query Tool.
2. **Write SQL**: Use the editor pane to type your queries.
3. **Execute**: Click ▶️ or press **F5**.
4. **View Results**: Results appear in the grid below.
5. **Save Queries**: File → Save Query (Ctrl+S).

## 4. Common SQL Queries

### 4.1 Inspect Row Counts

```sql
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = 'public';
```

### 4.2 View Sample Data

```sql
SELECT *
FROM users
LIMIT 5;
```

### 4.3 Join Areas with Users, Actions, Reactions

```sql
SELECT
  u.email        AS user_email,
  a.name         AS action_name,
  r.name         AS reaction_name,
  ar.status      AS area_status,
  ar.created_at  AS created_at
FROM areas ar
JOIN users u     ON ar.user_id     = u.id
JOIN actions a   ON ar.action_id   = a.id
JOIN reactions r ON ar.reaction_id = r.id
ORDER BY ar.created_at DESC;
```

### 4.4 List Parameters per Action

```sql
SELECT
  ac.name        AS action,
  p.name         AS parameter,
  ap.position,
  ap.required
FROM action_parameters ap
JOIN actions ac   ON ap.action_id    = ac.id
JOIN parameters p ON ap.parameter_id = p.id
ORDER BY ac.name, ap.position;
```

### 4.5 Check Quotas & Usage for User

```sql
SELECT
  u.email,
  q.period,
  q.max_executions,
  uc.executions,
  uc.period_start,
  uc.period_end
FROM quotas q
JOIN users u ON q.user_id = u.id
LEFT JOIN usage_counters uc
  ON q.user_id = uc.user_id
  AND q.period  = uc.period
WHERE u.email = 'alice@orga.com';
```

### 4.6 View Recent Execution Logs

```sql
SELECT
  el.occurred_at,
  el.status,
  el.duration_ms,
  el.error_message
FROM execution_logs el
JOIN areas ar ON el.area_id = ar.id
WHERE ar.user_id = (
  SELECT id FROM users WHERE email = 'alice@orga.com'
)
ORDER BY el.occurred_at DESC
LIMIT 10;
```

## 5. Executing Seed Data

Place your `seed.sql` in the project folder, then:

- **psql**:

  ```bash
  psql -h localhost -U myuser -d area_db -f seed.sql
  ```

- **Query Tool**:
  - File → Open → `seed.sql`
  - Execute ▶️

## 6. Exploring & Editing Data

- In your SQL client, under **Schemas → public → Tables**, right-click a table → **View/Edit Data → All Rows**.
- Modify values directly in the grid and click Save.

## 7. ERD Diagram

- Select multiple tables with Ctrl+Click.
- Right-click → **ERD for Selection** to visualize relationships.

## 8. Tips & Best Practices

- Alias columns with `AS` for clarity.
- Refresh table list after schema changes.
- Save and organize frequent queries in `.sql` files.
- Validate schema visually with ERD.
