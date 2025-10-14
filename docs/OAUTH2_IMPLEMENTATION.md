# OAuth2 Implementation - Backend-First Flow

## Overview

The AREA project uses a **Backend-First OAuth2 flow** for maximum security. All token handling is done server-side, ensuring that sensitive credentials (access tokens, refresh tokens) are never exposed to the frontend or mobile clients.

## Architecture

```
┌─────────┐     1. Click        ┌──────────┐    2. Generate    ┌─────────┐
│ Frontend│   "Connect Google"  │  Backend │    Auth URL       │  Google │
│         ├────────────────────>│   API    ├──────────────────>│  OAuth  │
└─────────┘                     └──────────┘                   └─────────┘
     │                                │                              │
     │  3. Redirect to Google         │                              │
     │<───────────────────────────────┘                              │
     │                                                               │
     │  4. User authorizes                                           │
     ├──────────────────────────────────────────────────────────────>│
     │                                                               │
     │                            5. Redirect with code & state      │
     │                            ┌──────────┐                       │
     │                            │  Backend │<──────────────────────┘
     │                            │ Callback │
     │                            └──────────┘
     │                                  │
     │                         6. Exchange code for token
     │                         7. Store in database
     │                         8. Redirect to frontend
     │  9. Show success       ┌──────────┐
     │<───────────────────────┤  Backend │
     │                        └──────────┘
```

## Components

### 1. Backend - OAuth Manager (`backend/users/oauth/`)

**Key Classes:**
- `BaseOAuthProvider`: Abstract base class (Template Method pattern)
- `GoogleOAuthProvider`: Google OAuth2 implementation
- `GitHubOAuthProvider`: GitHub OAuth2 implementation
- `OAuthManager`: Provider factory and token lifecycle management

**Key Features:**
- CSRF state generation with cryptographic randomness
- State validation with cache expiration (10 minutes)
- Automatic token refresh for expired tokens
- Provider-agnostic interface

### 2. Backend - OAuth Views (`backend/users/oauth_views.py`)

**Endpoints:**

#### `GET /auth/oauth/{provider}/`
Initiate OAuth2 flow. Returns authorization URL for user redirect.

**Request:**
```http
GET /auth/oauth/google/ HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "redirect_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "cryptographic_state_token",
  "provider": "google",
  "expires_in": 600
}
```

#### `GET /auth/oauth/{provider}/callback/`
Handle OAuth2 callback from provider. **Backend-First implementation**.

**Flow:**
1. Validates state token (CSRF protection)
2. Retrieves user from cached state data
3. Exchanges authorization code for access token
4. Stores token in database with metadata
5. Redirects to frontend with result

**Success Redirect:**
```
http://localhost:5173/auth/callback/google?success=true&service=google&created=true
```

**Error Redirect:**
```
http://localhost:5173/auth/callback/google?error=invalid_state&message=State+expired
```

#### `GET /auth/services/`
List connected services for the authenticated user.

**Response:**
```json
{
  "connected_services": [
    {
      "service_name": "google",
      "created_at": "2024-01-15T10:30:00Z",
      "expires_at": "2024-01-15T11:30:00Z",
      "is_expired": false,
      "scopes": "email profile https://www.googleapis.com/auth/gmail.readonly"
    }
  ],
  "available_providers": ["google", "github"],
  "total_connected": 1
}
```

#### `DELETE /auth/services/{provider}/disconnect/`
Disconnect a service and revoke tokens.

### 3. Database Model (`backend/users/models.py`)

**ServiceToken Model:**

```python
class ServiceToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)

    # Token data
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Metadata (Phase 1 enhancements)
    scopes = models.TextField(blank=True)  # Space-separated
    token_type = models.CharField(max_length=20, default="Bearer")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Tracks refreshes
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Properties
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""

    @property
    def needs_refresh(self) -> bool:
        """Check if token expires in < 5 minutes."""

    def mark_used(self) -> None:
        """Update last_used_at timestamp."""
```

### 4. Frontend - OAuth Hook (`frontend/src/hooks/useOAuth.ts`)

**Custom Hooks:**

```typescript
// Initiate OAuth flow
const { initiateOAuth, loading, error } = useInitiateOAuth();

// Usage
await initiateOAuth('google');  // Redirects to Google

// List connected services
const { services, availableProviders, loading } = useConnectedServices();

// Disconnect service
const { disconnectService, loading } = useDisconnectService();
await disconnectService('google');
```

### 5. Frontend - Callback Handler (`frontend/src/pages/OAuthCallback.tsx`)

Handles backend redirect after OAuth completion. Displays success/error and redirects to services page.

**Query Parameters:**
- Success: `?success=true&service=google&created=true`
- Error: `?error=invalid_state&message=State+expired`

## Security Features

### CSRF Protection
- Cryptographic state tokens (`secrets.token_urlsafe(32)`)
- State stored in Redis cache with 10-minute expiration
- One-time use validation (deleted after first check)
- State includes user_id and provider for verification

### Token Security
- Access tokens never exposed to frontend
- All token operations server-side only
- HTTPS enforced in production
- Token encryption at rest (database level)

### Automatic Token Refresh
```python
# Usage in tasks/services
from users.oauth.manager import OAuthManager

access_token = OAuthManager.get_valid_token(user, "google")
## Automatic Token Refresh

### Overview

AREA implements **proactive token refresh** to ensure seamless operation:

- **Automatic Detection**: Tokens expiring within 5 minutes are automatically refreshed
- **Zero Downtime**: Refresh happens before expiration, preventing API call failures
- **Transparent to Tasks**: `OAuthManager.get_valid_token()` handles everything
- **User Notifications**: Users are notified if refresh fails

### How It Works

```python
# When you call get_valid_token(), the system:
# 1. Checks if token is expired OR expiring within 5 minutes
# 2. If yes, attempts to refresh using refresh_token
# 3. Updates database with new token and expiration
# 4. Marks token as recently used
# 5. Returns valid access token

access_token = OAuthManager.get_valid_token(user, "google")
```

### Token Lifecycle

```
Token Created
    ↓
[Valid Period]
    ↓
5 min before expiry → Proactive Refresh Triggered
    ↓
Refresh Successful? → Yes → Token Updated → Continue
    ↓
    No → Notification Created → User Must Reconnect
```

### Usage in Tasks

```python
from users.oauth.manager import OAuthManager

@shared_task(name="automations.check_gmail_actions")
def check_gmail_actions():
    """
    Check for new Gmail messages.

    Token refresh is handled automatically by OAuthManager.
    """
    areas = Area.objects.filter(
        status=Area.Status.ACTIVE,
        action__name="gmail_new_email"
    ).select_related("owner")

    for area in areas:
        # Get valid token - automatically refreshes if needed
        access_token = OAuthManager.get_valid_token(area.owner, "google")

        if not access_token:
            # Token couldn't be refreshed - user has been notified
            logger.warning(
                f"No valid Google token for user {area.owner.id} "
                f"(AREA #{area.pk}). User notification created."
            )
            continue

        # Use token for API calls
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://www.googleapis.com/gmail/v1/users/me/messages",
            headers=headers,
            params={"maxResults": 10},
            timeout=10
        )
        # ... process response
```

## User Notifications

### Notification System

AREA automatically creates notifications when OAuth issues occur:

**Notification Types:**
- `TOKEN_EXPIRED`: Token has expired
- `REFRESH_FAILED`: Automatic refresh attempt failed
- `AUTH_ERROR`: Authentication error occurred
- `REAUTH_REQUIRED`: User must manually reconnect service

### API Endpoints

#### List Notifications
```http
GET /auth/notifications/
```

**Query Parameters:**
- `is_read`: Filter by read status (true/false)
- `is_resolved`: Filter by resolved status (true/false)
- `service_name`: Filter by service (google, github, etc.)

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "service_name": "google",
      "notification_type": "refresh_failed",
      "notification_type_display": "Token Refresh Failed",
      "message": "Your google connection has expired...",
      "is_read": false,
      "is_resolved": false,
      "created_at": "2025-10-13T10:30:00Z",
      "resolved_at": null,
      "time_since_created": "5 minutes ago"
    }
  ]
}
```

#### Mark Notification as Read
```http
POST /auth/notifications/{id}/mark_read/
```

#### Mark Notification as Resolved
```http
POST /auth/notifications/{id}/mark_resolved/
```

#### Get Unread Count
```http
GET /auth/notifications/unread_count/
```

**Response:**
```json
{
  "count": 3
}
```

#### Mark All as Read
```http
POST /auth/notifications/mark_all_read/
```

### Notification Resolution

Notifications are automatically resolved when:

1. **User Reconnects Service**: All notifications for that service are resolved
2. **Token Refresh Succeeds**: Related notifications are marked as resolved

### Frontend Integration Example

```typescript
// Fetch unread notifications
const fetchNotifications = async () => {
  const response = await fetch('/auth/notifications/?is_read=false', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  const data = await response.json();
  return data.results;
};

// Mark notification as read
const markAsRead = async (notificationId: number) => {
  await fetch(`/auth/notifications/${notificationId}/mark_read/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
};
```

## Token Health Monitoring

### Management Command

Check the health of all OAuth tokens across users:

```bash
# Basic health check
python manage.py check_token_health

# Check specific service
python manage.py check_token_health --service google

# Check and create notifications for users
python manage.py check_token_health --notify-users

# Verbose output
python manage.py check_token_health --verbose
```

### Example Output

```
=== OAuth Token Health Check ===

Filtering by service: google

Checking test@example.com/google...
  ✓ Healthy

Checking user2@example.com/google...
  ⚠️  Expires in 2.5 hours

Checking user3@example.com/google...
  ❌ EXPIRED
  ❌ No refresh token available
  ✉️  Created notification for user3@example.com

============================================================

📊 Summary:
  Total tokens: 10
  Healthy tokens: 7
  Expiring soon (< 24h): 2
  Expired tokens: 1
  Without refresh token: 1

❌ Expired Tokens:
  - user3@example.com/google (expired 2 days ago)

⚠️  Expiring Soon:
  - user2@example.com/google (expires in 2.5 hours)

🔄 Tokens Without Refresh Capability (require manual reauth):
  - user3@example.com/google

✉️  Created notifications for 1 users
```

### Scheduling Health Checks

Add to Celery Beat schedule for automated monitoring:

```python
# backend/area_project/celery.py

from celery.schedules import crontab

app.conf.beat_schedule = {
    # ... existing tasks ...

    'check-oauth-token-health': {
        'task': 'users.tasks.check_oauth_health',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'options': {'queue': 'default'},
    },
}
```

Create the task:

```python
# backend/users/tasks.py

from celery import shared_task
from django.core.management import call_command

@shared_task(name="users.check_oauth_health")
def check_oauth_health():
    """
    Check OAuth token health and notify users.

    Runs periodically to identify token issues proactively.
    """
    call_command('check_token_health', '--notify-users')
```

## Best Practices

### For Task Developers

1. **Always use `OAuthManager.get_valid_token()`**
   ```python
   # ✅ GOOD - Automatic refresh
   token = OAuthManager.get_valid_token(user, "google")
   if token:
       # Use token

   # ❌ BAD - Manual token access
   service_token = ServiceToken.objects.get(user=user, service_name="google")
   token = service_token.access_token  # Might be expired!
   ```

2. **Handle None gracefully**
   ```python
   token = OAuthManager.get_valid_token(user, "google")
   if not token:
       # User has been notified - just log and continue
       logger.warning(f"No valid token for {user.email}/google")
       return
   ```

3. **Don't retry on auth failures**
   ```python
   # The OAuthManager already tried to refresh
   # If it returns None, retrying won't help
   if not token:
       return  # Skip this execution
   ```

### For Service Owners

1. **Monitor token health regularly**
   ```bash
   # Weekly manual check
   python manage.py check_token_health --service myservice --verbose
   ```

2. **Set up automated monitoring**
   - Add Celery Beat schedule for periodic checks
   - Create alerts for high failure rates
   - Monitor notification creation rate

3. **Test token refresh flow**
   ```python
   # In your tests
   def test_token_refresh_flow(self):
       # Create expiring token
       token = ServiceToken.objects.create(
           user=self.user,
           service_name="myservice",
           expires_at=timezone.now() + timedelta(minutes=3),
           refresh_token="test_refresh"
       )

       # Should trigger refresh
       access_token = OAuthManager.get_valid_token(self.user, "myservice")
       self.assertIsNotNone(access_token)
   ```

## Troubleshooting

### Issue: Tokens not refreshing automatically

**Symptoms:**
- Tasks fail with 401 Unauthorized
- No notifications created
- Tokens show as expired in database

**Diagnosis:**
```python
python manage.py shell

>>> from users.models import ServiceToken
>>> token = ServiceToken.objects.get(user_id=..., service_name="google")
>>> print(f"Expired: {token.is_expired}")
>>> print(f"Needs refresh: {token.needs_refresh}")
>>> print(f"Has refresh token: {bool(token.refresh_token)}")
>>> print(f"Last used: {token.last_used_at}")
```

**Solutions:**
1. Check provider configuration has `requires_refresh: True`
2. Verify refresh token exists in database
3. Test refresh manually:
   ```python
   >>> from users.oauth.manager import OAuthManager
   >>> new_token = OAuthManager.refresh_if_needed(token)
   >>> print(new_token)
   ```

### Issue: Too many notifications created

**Symptoms:**
- Users receiving duplicate notifications
- Notification table growing rapidly

**Solutions:**
1. Check `create_notification()` deduplication logic
2. Resolve notifications when service reconnects
3. Clean up old resolved notifications:
   ```python
   # Delete resolved notifications older than 30 days
   from datetime import timedelta
   from django.utils import timezone
   from users.models import OAuthNotification

   cutoff = timezone.now() - timedelta(days=30)
   OAuthNotification.objects.filter(
       is_resolved=True,
       resolved_at__lt=cutoff
   ).delete()
   ```

### Issue: Token refresh succeeds but still fails

**Symptoms:**
- Logs show successful refresh
- API calls still return 401
- Token appears valid in database

**Diagnosis:**
- Check if provider rotates refresh tokens (some providers do)
- Verify scopes haven't changed
- Test token manually with provider's API

**Solution:**
```python
# Ensure refresh_if_needed saves rotated refresh tokens
# This is already implemented in Phase 2:
if "refresh_token" in refreshed:
    service_token.refresh_token = refreshed["refresh_token"]
```

if not access_token:
    # Token expired and refresh failed - notify user
    pass
```

## Configuration

### Environment Variables (`.env`)

```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/oauth/google/callback/

# GitHub OAuth2
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8080/auth/oauth/github/callback/

# Frontend URL for redirects
FRONTEND_URL=http://localhost:5173
```

### Django Settings (`backend/area_project/settings.py`)

```python
OAUTH2_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": ["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"],
        "requires_refresh": True,
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GITHUB_REDIRECT_URI"),
        "authorization_endpoint": "https://github.com/login/oauth/authorize",
        "token_endpoint": "https://github.com/login/oauth/access_token",
        "userinfo_endpoint": "https://api.github.com/user",
        "scopes": ["user", "repo", "notifications"],
        "requires_refresh": False,  # GitHub tokens don't expire
    },
}

# OAuth2 state expiry (seconds)
OAUTH2_STATE_EXPIRY = 600  # 10 minutes
```

## Adding a New Provider

### Step 1: Create Provider Class

```python
# backend/users/oauth/myprovider.py
from .base import BaseOAuthProvider

class MyProviderOAuthProvider(BaseOAuthProvider):
    def get_authorization_url(self, state: str) -> str:
        # Implementation
        pass

    def exchange_code_for_token(self, code: str) -> dict:
        # Implementation
        pass

    def refresh_access_token(self, refresh_token: str) -> dict:
        # Implementation
        pass

    def get_user_info(self, access_token: str) -> dict:
        # Implementation
        pass

    def revoke_token(self, token: str) -> bool:
        # Implementation
        pass
```

### Step 2: Register Provider

```python
# backend/users/oauth/manager.py
from .myprovider import MyProviderOAuthProvider

class OAuthManager:
    _provider_classes = {
        "google": GoogleOAuthProvider,
        "github": GitHubOAuthProvider,
        "myprovider": MyProviderOAuthProvider,  # Add here
    }
```

### Step 3: Add Configuration

```python
# backend/area_project/settings.py
OAUTH2_PROVIDERS = {
    # ... existing providers
    "myprovider": {
        "client_id": os.getenv("MYPROVIDER_CLIENT_ID", ""),
        "client_secret": os.getenv("MYPROVIDER_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("MYPROVIDER_REDIRECT_URI"),
        "authorization_endpoint": "https://myprovider.com/oauth/authorize",
        "token_endpoint": "https://myprovider.com/oauth/token",
        "scopes": ["read", "write"],
        "requires_refresh": True,
    },
}
```

### Step 4: Update Frontend

```typescript
// frontend/src/pages/serviceDetail.tsx
const oauthProviders = ['github', 'google', 'gmail', 'myprovider'];
```

## Testing

### Run OAuth Tests

```bash
# All OAuth tests
cd backend
python manage.py test users.tests.test_oauth
python manage.py test users.tests.test_oauth_callback_flow

# Specific test
python manage.py test users.tests.test_oauth_callback_flow.OAuthCallbackBackendFirstTestCase.test_successful_oauth_callback
```

### Manual Testing Flow

1. Start services:
   ```bash
   docker-compose up
   ```

2. Login to frontend (http://localhost:5173)

3. Navigate to Services page

4. Click "Connect Google" or "Connect GitHub"

5. Authorize on provider's page

6. Verify redirect to callback page with success

7. Check database:
   ```bash
   docker exec -it area_server python manage.py shell
   >>> from users.models import ServiceToken
   >>> ServiceToken.objects.all()
   ```

## Troubleshooting

### Issue: "State invalid or expired"

**Cause:** State token expired (> 10 minutes) or Redis cache cleared.

**Solution:**
- Restart OAuth flow
- Check Redis is running: `docker-compose ps redis`
- Verify `OAUTH2_STATE_EXPIRY` setting

### Issue: "Token exchange failed"

**Cause:** Invalid OAuth credentials or redirect URI mismatch.

**Solution:**
- Verify credentials in `.env`
- Check redirect URI matches exactly in OAuth provider console
- Ensure `FRONTEND_URL` is correct

### Issue: Tokens not refreshing

**Cause:** Provider doesn't support refresh or refresh token missing.

**Solution:**
- Check `requires_refresh` in provider config
- Verify refresh token stored in database
- GitHub doesn't support refresh (tokens are long-lived)

## Migration from Old Flow

If you have the old dual-mode (API + Browser) OAuth flow:

### Changes Made in Phase 1:

1. **Removed dual-mode detection** - Now always uses Backend-First flow
2. **Enhanced ServiceToken model** - Added scopes, token_type, updated_at, last_used_at
3. **Simplified frontend callback** - Only handles backend redirects
4. **Created migration** - `0005_enhance_servicetoken_model`

### To Apply:

```bash
# 1. Pull latest changes
git pull origin fix(frontend)--areaction

# 2. Run migration
cd backend
python manage.py migrate users

# 3. Clear old state cache (optional)
docker exec -it area_redis redis-cli FLUSHDB

# 4. Restart services
docker-compose restart
```

## Best Practices

1. **Always use HTTPS in production** - OAuth requires secure transport
2. **Rotate client secrets regularly** - Update every 90 days
3. **Monitor token expiration** - Set up alerts for refresh failures
4. **Log OAuth errors** - Track failed authentications
5. **Request minimal scopes** - Only request permissions you need
6. **Handle token refresh proactively** - Refresh before expiration (5 min threshold)

## Resources

- [OAuth2 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [Google OAuth2 Docs](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Docs](https://docs.github.com/en/developers/apps/building-oauth-apps)
