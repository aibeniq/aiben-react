# 401 Unauthorized Error Troubleshooting Guide

## Overview

A "401 Unauthorized" error occurs when a user attempts to access your AiBeniq application but fails authentication. This guide explains the possible causes and solutions for this error in your multi-layered authentication system.

**Common Scenarios**:

- **System-wide**: All users affected (usually server configuration issues)
- **One user affected**: Most likely browser-cached wrong HTTP Basic Auth credentials
- **Intermittent**: Network or rate limiting issues
- **After login**: JWT token or account issues

**Quick Fix for Single User Issues**: If only one person gets 401 errors, have them clear browser data or try incognito mode first - this resolves 90% of single-user 401 issues.

## Authentication Architecture

Your application uses a **multi-layered authentication system**:

1. **HTTP Basic Auth** (Traefik reverse proxy level)
2. **JWT Token Authentication** (Backend API level)
3. **Rate Limiting** (Multiple layers)
4. **Account Lockout Protection** (Database level)

## Possible Causes of 401 Errors

### 1. HTTP Basic Authentication Failure (Most Common)

**Description**: The first authentication layer is HTTP Basic Auth configured at the Traefik reverse proxy level.

**Symptoms**:

- Error occurs immediately when accessing the site
- Browser prompts for username/password
- No access to login page

**Possible Causes**:

- Incorrect credentials in `.htpasswd` file
- Missing or corrupted `.htpasswd` file
- Traefik middleware configuration issues
- Environment variables not set correctly (`USERNAME`, `HASHED_PASSWORD`)

**Solutions**:

- Verify `.htpasswd` file exists and contains correct credentials
- Check Traefik logs: `docker-compose logs traefik`
- Verify environment variables in `.env` file
- Restart Traefik: `docker-compose restart traefik`

### 2. Rate Limiting Triggered

**Description**: Multiple rate limiting layers protect against abuse.

**Rate Limiting Thresholds**:
| Layer | Type | Limit | Burst | Time Window |
|-------|------|-------|-------|-------------|
| Traefik (Auth) | IP-based | 10 req | 20 | 1 minute |
| Nginx | IP-based | 10 req/s | 20 | 1 second |
| Backend API | IP + User | 5 attempts | - | 15 minutes |
| Account Lockout | User | 5 failures | - | 1 hour lockout |

**Symptoms**:

- Error occurs after multiple rapid requests
- Works after waiting period
- May see "429 Too Many Requests" instead of 401

**Solutions**:

- Wait for rate limit to reset (typically 1-15 minutes)
- Check rate limit logs in backend
- Clear rate limit counters if needed (admin access required)

### 3. Invalid or Expired JWT Token

**Description**: After HTTP Basic Auth, users authenticate with JWT tokens stored in HTTP-only cookies.

**Symptoms**:

- Can access login page but gets 401 after login
- Error occurs on API calls after initial login
- Works after clearing cookies and re-login

**Possible Causes**:

- Token expired (default: 30 minutes)
- Token corrupted or tampered with
- Clock skew between client/server
- SECRET_KEY changed without proper rotation

**Solutions**:

- Clear browser cookies and re-login
- Check `ACCESS_TOKEN_EXPIRE_MINUTES` setting
- Verify server time synchronization
- Check backend logs for token validation errors

### 4. Account Lockout

**Description**: Accounts are automatically locked after 5 consecutive failed login attempts.

**Symptoms**:

- Login attempts consistently fail with 401/423 errors
- Error message mentions "account locked"
- Lockout lasts 1 hour

**Solutions**:

- Wait 1 hour for automatic unlock
- Contact administrator to manually unlock account
- Use admin utility: `python backend/manage_lockouts.py`

### 5. Inactive User Account

**Description**: User accounts can be deactivated by administrators.

**Symptoms**:

- Login succeeds but subsequent API calls fail with 401
- Account appears in database but marked inactive

**Solutions**:

- Contact administrator to reactivate account
- Check user status in database
- Verify `is_active` flag in user table

### 6. Backend Authentication Issues

**Description**: Issues with the login endpoint or user database.

**Symptoms**:

- Login form accepts credentials but returns 401
- Password reset doesn't work
- New user registration fails

**Possible Causes**:

- Database connection issues
- User database corrupted
- Password hashing problems
- SMTP configuration for password reset

**Solutions**:

- Check backend logs: `docker-compose logs backend`
- Verify database connectivity
- Test user creation and authentication
- Check SMTP settings for password recovery

### 7. Network and Proxy Issues

**Description**: Issues with request routing or cookie handling.

**Symptoms**:

- Intermittent 401 errors
- Works on some devices/networks but not others
- CORS-related issues

**Solutions**:

- Check `BACKEND_CORS_ORIGINS` settings
- Verify cookie domain/path settings
- Check proxy headers (X-Forwarded-For)
- Test with different browsers/devices

### 8. User-Specific Issues (One User Affected)

**Description**: When only one user experiences 401 errors while others can access the site normally, the issue is typically client-side or user-specific rather than server-wide.

**Symptoms**:

- Only one team member gets 401 errors
- Everyone else can access the site normally
- Same user works on different devices/browsers
- Issue persists across browser sessions

#### A. Browser-Cached HTTP Basic Auth Credentials

**Most Common Cause**: Browsers cache HTTP Basic Authentication credentials and automatically send them with every request to the domain. If incorrect credentials were entered previously, the browser will continue sending them until cleared.

**Symptoms**:

- Browser shows login prompt briefly, then immediately shows 401 error
- No opportunity to re-enter credentials
- Issue persists after page refresh

**Solutions**:

**For Chrome/Chromium browsers**:

1. Click the lock icon in the address bar (or "i" icon on mobile)
2. Click "Site settings"
3. Scroll down and click "Clear data" or "Reset permissions"
4. Or: Go to `chrome://settings/clearBrowserData` and clear "Cached images and files"

**For Firefox**:

1. Click the lock icon in the address bar
2. Click the arrow next to the connection type
3. Click "More Information" → "Security" tab → "View Saved Passwords"
4. Remove the entry for your domain
5. Or: Go to `about:preferences#privacy` → "Cookies and Site Data" → "Manage Data"

**For Safari**:

1. Safari → Preferences → Privacy → Manage Website Data
2. Search for your domain and remove it
3. Or: Develop menu → Empty Caches (if enabled)

**For Edge**:

1. Click the lock icon in address bar → "Cookies and site permissions"
2. Click "Cookies and data stored" → "Manage and delete cookies and site data"
3. Remove data for your domain

**Alternative Solutions**:

- **Incognito/Private browsing mode**: Opens a fresh session without cached credentials
- **Different browser**: Test with Chrome/Firefox/Edge to isolate browser-specific issues
- **Clear all browser data**: Settings → Privacy → Clear browsing data (include "Cached images and files" and "Cookies and other site data")

#### B. User Account-Specific Issues

**Possible Causes**:

- User's account is locked due to failed login attempts
- User's account is marked inactive
- User's IP address is rate limited
- User's browser blocks cookies or has security settings that interfere

**Solutions**:

- Check if the user's account is locked: Query database for `failed_login_attempts` and `locked_until`
- Verify user's IP isn't rate limited: Check rate limiting logs
- Test with different network (mobile hotspot) to rule out IP blocking
- Ensure browser accepts cookies and JavaScript

#### C. Device/Browser Configuration Issues

**Possible Causes**:

- Browser security settings blocking authentication
- VPN/proxy interfering with requests
- Corporate firewall blocking authentication headers
- Browser extensions interfering with authentication
- Outdated browser or incompatible settings

**Solutions**:

- Disable browser extensions temporarily
- Try without VPN/proxy
- Test on different network
- Update browser to latest version
- Check browser security settings

#### D. Cookie/Session Issues

**Symptoms**:

- User can access login page but gets 401 on API calls
- Works after clearing cookies

**Solutions**:

- Clear all cookies for the domain
- Check browser cookie settings
- Verify cookie domain/path matches server configuration

## Diagnostic Steps

### 1. Check Logs

```bash
# Traefik logs
docker-compose logs traefik

# Backend logs
docker-compose logs backend

# Nginx logs (if using nginx config)
docker-compose logs frontend
```

### 2. Verify Configuration

```bash
# Check environment variables
cat .env | grep -E "(USERNAME|PASSWORD|SECRET_KEY)"

# Verify .htpasswd exists
ls -la frontend/.htpasswd

# Check Traefik configuration
docker-compose config
```

### 3. Test Authentication Flow

```bash
# Test HTTP Basic Auth
curl -u username:password https://your-domain.com

# Test API login
curl -X POST https://your-api-domain.com/api/v1/login/access-token \
  -d "username=user@example.com&password=password"

# Test token validation
curl https://your-api-domain.com/api/v1/login/test-token \
  -H "Cookie: access_token=your_token"
```

### 4. Database Checks

```bash
# Check user status
docker-compose exec db psql -U postgres -d your_db -c "SELECT email, is_active, failed_login_attempts, locked_until FROM users;"

# Check recent failed attempts
docker-compose logs backend | grep "failed.login"
```

## Prevention

### 1. Monitor Authentication Logs

- Set up log aggregation and alerting
- Monitor for unusual login patterns
- Track rate limiting triggers

### 2. Regular Maintenance

- Rotate passwords regularly
- Clean up old/inactive accounts
- Update rate limiting thresholds as needed

### 3. Backup and Recovery

- Regular database backups
- Document recovery procedures
- Test authentication failover scenarios

## Emergency Access

If all authentication is broken:

1. Access database directly via adminer (`alaco-adminer.your-domain.com`)
2. Reset user passwords or unlock accounts
3. Check/recreate `.htpasswd` file
4. Restart services: `docker-compose restart`

## Support

For persistent issues:

1. Collect logs from all services
2. Note exact error messages and timing
3. Document steps to reproduce
4. Contact system administrator with diagnostic information</content>
   <parameter name="filePath">c:\miniconda\aibeniq-react\401_UNAUTHORIZED_TROUBLESHOOTING.md
