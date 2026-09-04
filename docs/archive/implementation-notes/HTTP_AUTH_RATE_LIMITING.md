# HTTP Basic Auth Rate Limiting Implementation

**Date:** October 12, 2025  
**Issue:** Protecting HTTP Basic Authentication from brute-force attacks  
**Status:** ✅ IMPLEMENTED

---

## Overview

This implementation adds **multi-layer rate limiting** to protect the HTTP Basic Authentication (Traefik BasicAuth) from brute-force attacks. The protection works at both the Traefik reverse proxy level and the Nginx web server level.

---

## Architecture

```
Internet → Traefik (Rate Limit + HTTP Basic Auth) → Nginx (Rate Limit) → Frontend App
                ↓
          Backend API (Rate Limit + App-level Auth with Account Lockout)
```

### Layer 1: Traefik Rate Limiting
- **Location:** Reverse proxy / Load balancer
- **Protects:** HTTP Basic Auth login attempts
- **Limits:** 10 requests/minute with burst of 20

### Layer 2: Nginx Rate Limiting  
- **Location:** Web server
- **Protects:** Static file access and general requests
- **Limits:** 10 requests/second with burst of 20

### Layer 3: Application Rate Limiting
- **Location:** FastAPI backend
- **Protects:** User login endpoint
- **Limits:** 5 attempts per 15 minutes + account lockout

---

## Implementation Details

### 1. Traefik Configuration

**File:** `docker/traefik-rate-limit.yml`

```yaml
http:
  middlewares:
    auth-ratelimit:
      rateLimit:
        average: 10      # 10 requests per second
        period: 1m       # Per minute
        burst: 20        # Allow burst
```

**Applied to:**
- Frontend HTTPS route (with HTTP Basic Auth)
- Backend API routes (general protection)

### 2. Nginx Configuration

**File:** `frontend/nginx.conf`

```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

server {
    location / {
        limit_req zone=general_limit burst=20 nodelay;
        # ... rest of config
    }
}
```

### 3. Application-Level Protection

**File:** `backend/app/api/routes/login.py`

Already implemented with:
- IP-based rate limiting (5 attempts per 15 minutes)
- Username-based rate limiting
- Database-backed account lockout

---

## Rate Limiting Thresholds

| Layer | Type | Limit | Burst | Time Window | When Triggered |
|-------|------|-------|-------|-------------|----------------|
| **Traefik (Auth)** | IP-based | 10 req | 20 | 1 minute | Before HTTP Basic Auth |
| **Nginx** | IP-based | 10 req/s | 20 | 1 second | After auth, before app |
| **Backend API** | IP + User | 5 attempts | - | 15 minutes | On login endpoint |
| **Account Lockout** | User | 5 failures | - | - | 1 hour lockout |

---

## HTTP Status Codes

| Code | Meaning | Source | Action |
|------|---------|--------|--------|
| **429** | Too Many Requests | Traefik/Nginx/Backend | Rate limit hit, wait and retry |
| **401** | Unauthorized | Traefik BasicAuth | Wrong HTTP password |
| **423** | Locked | Backend | Account locked, wait 1 hour |

---

## Testing

### Test Traefik Rate Limiting

```bash
# Test HTTP Basic Auth rate limiting
for i in {1..15}; do
  echo "Attempt $i:"
  curl -i -u "wrong:password" https://alaco.yourdomain.com/ 2>&1 | grep "HTTP/"
  sleep 1
done

# Expected: First ~10 attempts get 401 (wrong password)
#          After that, you'll get 429 (rate limited)
```

### Test Nginx Rate Limiting

```bash
# Make rapid requests
for i in {1..30}; do
  curl -i -u "alaco:correctpassword" https://alaco.yourdomain.com/ \
    -w "\n%{http_code}\n" -o /dev/null 2>&1 | tail -1
done

# Expected: First ~20-30 succeed (200), then 429
```

### Test Backend API Rate Limiting

```bash
# Test login endpoint (already tested in previous implementation)
./test_rate_limit.sh
```

---

## Monitoring

### Check Traefik Access Logs

```bash
# View rate limit events
docker-compose logs traefik | grep "429"

# Count 429 responses
docker-compose logs traefik | grep "429" | wc -l
```

### Check Nginx Logs

```bash
# View nginx rate limit logs
docker-compose logs frontend | grep "limiting requests"

# Check specific IP
docker-compose logs frontend | grep "limiting requests" | grep "192.168.1.100"
```

### Metrics to Track

1. **429 responses per hour** - Track rate limit hits
2. **401 responses per hour** - Track failed auth attempts  
3. **Top IPs hitting rate limits** - Identify attackers
4. **Geographic distribution** - Unusual locations
5. **Time patterns** - Automated attacks often show patterns

---

## Configuration

### Adjust Traefik Rate Limits

Edit `docker/traefik-rate-limit.yml`:

```yaml
auth-ratelimit:
  rateLimit:
    average: 5       # More strict: 5 requests
    period: 1m       # Per minute
    burst: 10        # Lower burst
```

### Adjust Nginx Rate Limits

Edit `frontend/nginx.conf`:

```nginx
# More strict
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=5r/s;

# More permissive
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=20r/s;
```

### Apply Changes

```bash
# Restart services to apply new config
docker-compose down
docker-compose up -d

# Or just restart specific services
docker-compose restart traefik
docker-compose restart frontend
```

---

## Security Benefits

### Protection Against:

| Attack Type | Protection Layer | Effectiveness |
|-------------|------------------|---------------|
| **HTTP Basic Auth Brute Force** | Traefik rate limit | ✅ Blocks after 10/min |
| **Distributed Attacks** | Multiple IP detection | ✅ Each IP limited separately |
| **Application Login Brute Force** | Backend rate limit | ✅ Account lockout after 5 |
| **DoS via Auth Requests** | Traefik + Nginx | ✅ Resource protection |
| **Credential Stuffing** | All layers | ✅ Multi-layer defense |

---

## Additional Security Headers

The implementation also adds security headers via Traefik:

```yaml
security-headers:
  headers:
    sslRedirect: true
    stsSeconds: 31536000              # HSTS
    stsIncludeSubdomains: true
    frameDeny: true                   # Clickjacking protection
    contentTypeNosniff: true          # MIME sniffing protection
    browserXssFilter: true            # XSS protection
```

---

## Troubleshooting

### Issue: Legitimate users getting rate limited

**Solution 1:** Increase burst limits
```yaml
burst: 50  # Allow more burst traffic
```

**Solution 2:** Add IP whitelist for known IPs
```yaml
ip-whitelist:
  ipWhiteList:
    sourceRange:
      - "YOUR_OFFICE_IP/32"
```

### Issue: Rate limiting not working

**Check Traefik config:**
```bash
# Verify dynamic config is loaded
docker-compose exec traefik cat /etc/traefik/dynamic/rate-limit.yml

# Check Traefik logs for errors
docker-compose logs traefik | grep -i error
```

**Check Nginx config:**
```bash
# Test nginx configuration
docker-compose exec frontend nginx -t

# Reload nginx
docker-compose exec frontend nginx -s reload
```

### Issue: Want to temporarily disable rate limiting

**Traefik:** Comment out middleware in docker-compose.yml:
```yaml
# - traefik.http.routers.frontend-https.middlewares=...,auth-ratelimit@file,...
```

**Nginx:** Comment out limit_req directive:
```nginx
# limit_req zone=general_limit burst=20 nodelay;
```

---

## Best Practices

1. **Monitor regularly** - Set up alerts for high 429 counts
2. **Review logs weekly** - Look for attack patterns
3. **Adjust limits** - Based on legitimate traffic patterns
4. **Use strong passwords** - Even with rate limiting
5. **Consider VPN** - For infrastructure access instead of HTTP Basic Auth
6. **Rotate credentials** - Change HTTP Basic Auth password periodically

---

## Future Enhancements

### Recommended:

1. **GeoIP Blocking** - Block requests from suspicious countries
   ```yaml
   geoip-block:
     plugin:
       geoblock:
         allowedCountries:
           - "US"
           - "GB"
           - "DE"
   ```

2. **WAF Integration** - Add ModSecurity or Cloudflare WAF

3. **Metrics Dashboard** - Prometheus + Grafana for visualization

4. **Automated Banning** - Fail2ban integration with Traefik

5. **2FA for HTTP Auth** - Use OAuth2 Proxy instead of Basic Auth

---

## Compliance

This implementation helps meet:
- ✅ **OWASP Top 10** - A07:2021 Identification and Authentication Failures
- ✅ **PCI DSS** - Requirement 8.1.6 (limit repeated access attempts)
- ✅ **NIST 800-63B** - Rate limiting on authentication
- ✅ **GDPR** - Security of processing (Article 32)

---

## Files Modified/Created

### Created:
1. ✅ `docker/traefik-rate-limit.yml` - Traefik rate limiting config
2. ✅ `HTTP_AUTH_RATE_LIMITING.md` - This documentation

### Modified:
1. ✅ `frontend/nginx.conf` - Added nginx rate limiting
2. ✅ `docker-compose.traefik.yml` - Enabled file provider
3. ✅ `docker-compose.yml` - Applied rate limit middlewares

---

## Summary

✅ **Multi-layer rate limiting** - Traefik + Nginx + Application  
✅ **HTTP Basic Auth protected** - 10 attempts/minute  
✅ **General traffic limited** - 10 req/sec with burst  
✅ **Security headers added** - HSTS, XSS, Clickjacking protection  
✅ **Production ready** - Tested and documented  
✅ **Monitoring enabled** - Via Traefik/Nginx logs  

**Result:** HTTP Basic Authentication is now protected against brute-force attacks with industry-standard rate limiting at multiple levels.

---

**Questions?** Check Traefik logs or contact the security team.

**Emergency disable:** Comment out middlewares in docker-compose.yml and restart services.
