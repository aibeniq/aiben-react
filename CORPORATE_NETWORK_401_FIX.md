# Fix: 401 Errors for Corporate Network Users

## Problem Summary

Users accessing from corporate networks get 401 errors while personal devices work fine. This is caused by **IP-based rate limiting** when multiple employees share the same corporate proxy/NAT IP address.

## Root Cause

Your application has aggressive IP-based rate limiting:

- **Traefik**: 10 requests/minute per IP
- **Backend**: 5 login attempts per 15 minutes per IP

When 10+ employees access from the same corporate IP, they hit rate limits collectively.

## Recommended Solution

**Remove IP-based rate limiting at Traefik level, keep user-based rate limiting at backend level.**

This allows multiple corporate users while still preventing brute force attacks on individual accounts.

---

## Implementation Steps

### Step 1: Remove Traefik HTTP Basic Auth Rate Limiting

**File**: `docker-compose.yml`

**Find** (around line 212):

```yaml
- traefik.http.routers.${STACK_NAME?Variable not set}-frontend-https.middlewares=${STACK_NAME?Variable not set}-auth,auth-ratelimit@file,security-headers@file
```

**Replace with**:

```yaml
- traefik.http.routers.${STACK_NAME?Variable not set}-frontend-https.middlewares=${STACK_NAME?Variable not set}-auth,security-headers@file
```

**What changed**: Removed `auth-ratelimit@file` from the middleware chain.

---

### Step 2: Disable IP-Based Rate Limiting in Backend (Optional but Recommended)

**File**: `backend/app/api/routes/login.py`

**Find** (around line 44-48):

```python
# Get client IP for rate limiting
client_ip = get_client_ip(request)

# Rate limit by IP address
await rate_limiter.check_rate_limit(f"ip:{client_ip}")

# Rate limit by username (email)
await rate_limiter.check_rate_limit(f"user:{form_data.username}")
```

**Replace with**:

```python
# Get client IP for rate limiting (still used for logging/auditing)
client_ip = get_client_ip(request)

# Skip IP-based rate limiting to allow corporate networks with shared IPs
# Only rate limit by username to prevent brute force on individual accounts
await rate_limiter.check_rate_limit(f"user:{form_data.username}")
```

**What changed**: Commented out IP-based rate limiting, kept user-based rate limiting.

---

### Step 3: Keep Backend Rate Limiting Active

**No changes needed** - Your backend already has strong per-user protections:

✅ **User-based rate limiting**: 5 attempts per 15 minutes per username  
✅ **Account lockout**: 5 failed login attempts = 1 hour lockout  
✅ **Failed attempt tracking**: Database-backed, survives restarts

These protections prevent brute force attacks **without blocking corporate users**.

---

### Step 4: Apply Changes

```powershell
# Restart services to apply changes
docker-compose restart traefik
docker-compose restart backend

# Verify services are running
docker-compose ps

# Check logs for any errors
docker-compose logs traefik --tail=50
docker-compose logs backend --tail=50
```

---

## Testing

### Test 1: Verify Rate Limiting Removed

```powershell
# Have affected users try accessing the site from work computers
# Should work now without 401 errors
```

### Test 2: Verify Security Still Active

```bash
# Test that user-based rate limiting still works
# Try logging in with wrong password 6 times - should get locked out

curl -X POST https://your-api-domain.com/api/v1/login/access-token \
  -d "username=test@example.com&password=wrongpassword"

# After 5 attempts, should get 423 Locked error
```

### Test 3: Monitor Logs

```powershell
# Watch for rate limiting events (should be user-based only)
docker-compose logs backend -f | Select-String "rate limit"

# Watch for failed login attempts
docker-compose logs backend -f | Select-String "failed login"
```

---

## Alternative Solutions (If Issues Persist)

### Option A: Whitelist Corporate IP

If you want to keep strict rate limiting but allow your corporate network:

**File**: `docker/traefik-rate-limit.yml`

Add your corporate IP to the whitelist:

```yaml
ip-whitelist:
  ipWhiteList:
    sourceRange:
      - "127.0.0.1/32"
      - "10.0.0.0/8"
      - "172.16.0.0/12"
      - "192.168.0.0/16"
      - "YOUR_CORPORATE_PUBLIC_IP/32" # Add this line
```

Then apply to frontend in `docker-compose.yml`:

```yaml
- traefik.http.routers.${STACK_NAME}-frontend-https.middlewares=${STACK_NAME}-auth,ip-whitelist@file,security-headers@file
```

**How to find corporate public IP**:

```powershell
# Ask affected user to visit from work computer:
# https://whatismyipaddress.com/
```

### Option B: Increase Rate Limits

**File**: `docker/traefik-rate-limit.yml`

```yaml
auth-ratelimit:
  rateLimit:
    average: 100 # Increase from 10 to 100
    period: 1m
    burst: 200 # Increase from 20 to 200
```

---

## Rollback Plan

If the fix causes issues:

```powershell
# Rollback Step 1: Re-enable Traefik rate limiting
# Edit docker-compose.yml and add back auth-ratelimit@file

# Rollback Step 2: Re-enable backend IP rate limiting
# Uncomment the IP rate limit line in login.py

# Restart services
docker-compose restart traefik backend
```

---

## Monitoring After Fix

### Check Rate Limiting Activity

```powershell
# Should only see user-based rate limiting now
docker-compose logs backend | Select-String "rate limit.*user:"

# Should NOT see IP-based rate limiting
docker-compose logs backend | Select-String "rate limit.*ip:"
```

### Check Account Lockouts

```powershell
# Check database for locked accounts
docker-compose exec db psql -U postgres -d your_db -c "SELECT email, failed_login_attempts, locked_until FROM users WHERE locked_until IS NOT NULL;"
```

### Monitor Failed Logins

```powershell
# Track failed login patterns
docker-compose logs backend | Select-String "Incorrect email or password"
```

---

## Security Notes

### What We're Removing:

- ❌ IP-based rate limiting at Traefik (HTTP Basic Auth layer)
- ❌ IP-based rate limiting at backend (optional)

### What We're Keeping:

- ✅ HTTP Basic Auth still required (username/password)
- ✅ User-based rate limiting (5 attempts per 15 min per user)
- ✅ Account lockout after 5 failed attempts (1 hour)
- ✅ Database-backed failed attempt tracking
- ✅ General traffic rate limiting (100 req/s at Traefik)
- ✅ Security headers (HSTS, XSS protection, etc.)

**This configuration maintains strong security while allowing corporate network access.**

---

## Expected Results

After implementing this fix:

✅ Corporate users can access site from work computers  
✅ Personal devices continue working  
✅ Individual accounts still protected from brute force  
✅ No more shared IP rate limiting issues  
✅ Maintains overall system security

---

## Support

If issues persist after implementing these changes:

1. Check Traefik logs: `docker-compose logs traefik | Select-String "401"`
2. Check backend logs: `docker-compose logs backend | Select-String "rate limit"`
3. Verify middleware configuration: `docker-compose config | Select-String "middleware"`
4. Contact system administrator with diagnostic information
