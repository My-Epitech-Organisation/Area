# OAuth2 Integration - AREA Project

## Overview

The AREA project now supports OAuth2 authentication with external services, allowing users to securely connect their Google and GitHub accounts to enable powerful automations.

## Supported Providers

- **Google** (Gmail, Google Calendar, Drive)
  - Supports token refresh
  - Scopes: `openid`, `email`, `profile`, `gmail.readonly`

- **GitHub** (Repositories, Issues, Notifications)
  - Long-lived tokens (no expiration)
  - Scopes: `user`, `repo`, `notifications`

## User Flow

### 1. Register/Login
```bash
POST /auth/register/
POST /auth/login/
```

### 2. Connect a Service

#### Step 1: Initiate OAuth2 Flow
```bash
GET /auth/oauth/{provider}/

# Example: Connect Google
GET /auth/oauth/google/
```

**Response:**
```json
{
  "redirect_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "state": "abc123...",
  "provider": "google",
  "expires_in": 600
}
```

#### Step 2: User Authorizes
The user is redirected to the provider (Google/GitHub) and authorizes access.

#### Step 3: Callback Handling
After authorization, the provider redirects back to:
```bash
GET /auth/oauth/{provider}/callback/?code=xxx&state=yyy
```

The backend automatically:
- Validates the state (CSRF protection)
- Exchanges the code for an access token
- Stores the token securely in the database

**Response:**
```json
{
  "message": "Successfully connected to google",
  "service": "google",
  "created": true,
  "expires_at": "2025-10-06T15:30:00Z"
}
```

### 3. View Connected Services
```bash
GET /auth/services/
```

**Response:**
```json
{
  "connected_services": [
    {
      "service_name": "google",
      "created_at": "2025-10-06T10:00:00Z",
      "expires_at": "2025-10-06T15:30:00Z",
      "is_expired": false,
      "expires_in_minutes": 330,
      "has_refresh_token": true
    }
  ],
  "available_providers": ["google", "github"],
  "total_connected": 1
}
```

### 4. Create Areas with OAuth2 Services

When creating an Area that uses a service requiring OAuth2:

```bash
POST /api/areas/
{
  "name": "Email to GitHub Issue",
  "action": 5,  # Gmail action
  "reaction": 12,  # GitHub reaction
  "action_config": {},
  "reaction_config": {}
}
```

**Validation:**
- The backend checks if you have connected the required services
- If not connected, returns error with instructions

**Error Response (if not connected):**
```json
{
  "action": "You must connect your Google account before creating an area with this action. Please visit /auth/oauth/google/ to connect."
}
```

### 5. Disconnect a Service
```bash
DELETE /auth/services/{provider}/disconnect/

# Example
DELETE /auth/services/google/disconnect/
```

**Response:**
```json
{
  "message": "Successfully disconnected from google",
  "service": "google",
  "revoked_at_provider": true
}
```

## Token Management

### Automatic Token Refresh

The system automatically refreshes expired tokens (for providers that support it like Google):

- Tokens are checked before each API call
- If expired and refresh token is available, automatic refresh occurs
- If refresh fails, the Area execution is skipped

### Token Expiry Handling

- **Google**: Tokens expire after 1 hour, but are automatically refreshed
- **GitHub**: Tokens are long-lived (1 year) and don't require refresh

### Security

- **CSRF Protection**: State parameter validates OAuth2 callbacks
- **Token Storage**: Access and refresh tokens are stored encrypted in database
- **Scope Limitation**: Only request necessary scopes
- **Token Revocation**: Tokens are revoked at provider on disconnect

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/oauth/google/callback/

# GitHub OAuth2
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8080/auth/oauth/github/callback/
```

### Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google+ API** and **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Set **Authorized redirect URIs**:
   - `http://localhost:8080/auth/oauth/google/callback/`
   - `https://yourdomain.com/auth/oauth/google/callback/` (production)
6. Copy **Client ID** and **Client Secret** to `.env`

### GitHub OAuth App Setup

1. Go to GitHub **Settings** → **Developer settings** → **OAuth Apps**
2. Click **New OAuth App**
3. Fill in:
   - **Application name**: AREA
   - **Homepage URL**: `http://localhost:8080`
   - **Authorization callback URL**: `http://localhost:8080/auth/oauth/github/callback/`
4. Register application
5. Copy **Client ID** and generate **Client Secret**, add to `.env`

## Development

### Testing OAuth2 Locally

1. **Start the backend**:
   ```bash
   docker-compose up server
   ```

2. **Initiate OAuth2 flow**:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        http://localhost:8080/auth/oauth/google/
   ```

3. **Copy redirect_url** and open in browser
4. **Authorize** the application
5. **View connected services**:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        http://localhost:8080/auth/services/
   ```

### Running Tests

```bash
docker-compose exec server python manage.py test users.tests.test_oauth
```

## Architecture

### Provider Pattern

```
BaseOAuthProvider (Abstract)
├── GoogleOAuthProvider
└── GitHubOAuthProvider
```

Each provider implements:
- `get_authorization_url(state)` - Generate OAuth2 URL
- `exchange_code_for_token(code)` - Exchange code for token
- `refresh_access_token(refresh_token)` - Refresh expired token
- `get_user_info(access_token)` - Fetch user profile
- `revoke_token(token)` - Revoke access

### OAuthManager

Central manager that:
- Factory for provider instances
- Token lifecycle management
- Automatic token refresh
- CSRF state generation/validation

### Integration with Celery Tasks

Celery tasks use `OAuthManager.get_valid_token()` to:
1. Retrieve user's token for a service
2. Check if expired
3. Automatically refresh if needed
4. Return valid token or None

Example in `check_github_actions` task:
```python
access_token = OAuthManager.get_valid_token(area.owner, "github")
if not access_token:
    logger.warning("No valid GitHub token, skipping area")
    continue

# Use token for GitHub API
headers = {"Authorization": f"Bearer {access_token}"}
```

## API Reference

### POST /auth/oauth/{provider}/
Initiate OAuth2 authorization flow

**Path Parameters:**
- `provider`: `google` or `github`

**Response:** Authorization URL with state

---

### GET /auth/oauth/{provider}/callback/
OAuth2 callback endpoint (called by provider)

**Query Parameters:**
- `code`: Authorization code
- `state`: CSRF state token

**Response:** Success/error message

---

### GET /auth/services/
List connected services

**Response:** Array of connected services with expiry info

---

### DELETE /auth/services/{provider}/disconnect/
Disconnect a service

**Path Parameters:**
- `provider`: Service name to disconnect

**Response:** Confirmation message

## Troubleshooting

### "Invalid state parameter"
- State expired (10 minutes)
- CSRF attack attempt
- Clear cache and retry

### "Provider not configured"
- Check `.env` file has CLIENT_ID and CLIENT_SECRET
- Restart server after changing `.env`

### "Failed to refresh token"
- Refresh token invalid/revoked
- User needs to reconnect: `DELETE /auth/services/{provider}/disconnect/` then reconnect

### "You must connect your X account"
- User hasn't authorized the service
- Follow OAuth2 flow: `GET /auth/oauth/{provider}/`

## Future Enhancements

- [ ] Add more providers (LinkedIn, Twitter, Slack, Discord)
- [ ] Implement consent screen customization
- [ ] Add webhook notifications for token expiry
- [ ] Implement service health checks
- [ ] Add OAuth2 analytics dashboard

## Resources

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Apps](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Authlib Documentation](https://docs.authlib.org/)
