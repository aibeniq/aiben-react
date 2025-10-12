# Rate Limiting & Account Lockout - Quick Reference

## 🚨 For Developers

### What Changed?
The login endpoint now has **brute-force protection** with rate limiting and account lockout.

### Impact on Your Code
- ✅ **Frontend**: No changes needed - same API contract
- ✅ **Testing**: Use test accounts carefully (can get locked)
- ✅ **Error Handling**: Handle new 423 and 429 status codes

---

## 📝 New HTTP Status Codes

| Code | When | What to do |
|------|------|-----------|
| `423 Locked` | Account locked after 5 failed attempts | Show "Account locked, try again in X minutes" |
| `429 Too Many Requests` | Rate limit exceeded | Show "Too many attempts, please wait" |

---

## 🔧 Development Tips

### Unlock Your Test Account
```bash
# If you lock yourself out during testing
docker-compose exec backend python manage_lockouts.py --unlock your@email.com
```

### Disable Rate Limiting (Dev Only)
```python
# In login.py - comment these lines temporarily
# await rate_limiter.check_rate_limit(f"ip:{client_ip}")
# await rate_limiter.check_rate_limit(f"user:{form_data.username}")
```

### Check Lock Status
```bash
docker-compose exec backend python manage_lockouts.py --check your@email.com
```

---

## 🧪 Testing

### Frontend Test Cases

**Test 1: Normal login (should work)**
```javascript
// Single attempt with correct credentials
await login(email, correctPassword)
// Expected: 200 OK
```

**Test 2: Rate limit (should show error)**
```javascript
// 6 rapid attempts with wrong password
for (let i = 0; i < 6; i++) {
  await login(email, wrongPassword)
}
// Expected: 429 after 5th attempt
// Show: "Too many attempts, please wait"
```

**Test 3: Account lockout (should show locked)**
```javascript
// 5 failed attempts, then correct password
for (let i = 0; i < 5; i++) {
  await login(email, wrongPassword)
}
await login(email, correctPassword)
// Expected: 423 (still locked)
// Show: "Account locked for 1 hour"
```

### API Testing with curl

```bash
# Test rate limiting
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/login/access-token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test@example.com&password=wrong" \
    -w "\nHTTP: %{http_code}\n"
done
```

---

## 🎯 Frontend Error Handling

### Recommended User Messages

```typescript
switch (error.status) {
  case 423:
    // Account locked
    showError("Your account has been locked due to multiple failed login attempts. Please try again in 1 hour or contact support.")
    break
    
  case 429:
    // Rate limited
    showError("Too many login attempts. Please wait a few minutes and try again.")
    break
    
  case 400:
    // Wrong credentials
    showError("Invalid email or password. Please try again.")
    break
}
```

### Example React Hook

```typescript
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await loginApi(email, password)
    // Success
  } catch (error) {
    if (error.response?.status === 423) {
      setError("Account locked. Try again in 1 hour.")
      setShowContactSupport(true)
    } else if (error.response?.status === 429) {
      setError("Too many attempts. Wait 15 minutes.")
      setDisableLogin(true)
      setTimeout(() => setDisableLogin(false), 15 * 60 * 1000)
    } else {
      setError("Invalid credentials")
    }
  }
}
```

---

## 🛠️ Admin Tools

### Command Reference

```bash
# List all locked accounts
docker-compose exec backend python manage_lockouts.py --list

# Check specific account
docker-compose exec backend python manage_lockouts.py --check user@example.com

# Unlock specific account
docker-compose exec backend python manage_lockouts.py --unlock user@example.com

# Unlock all expired locks
docker-compose exec backend python manage_lockouts.py --unlock-expired
```

### Direct Database Queries

```sql
-- Find locked accounts
SELECT email, failed_login_attempts, locked_until 
FROM user 
WHERE locked_until IS NOT NULL;

-- Manually unlock account
UPDATE user 
SET failed_login_attempts = 0, locked_until = NULL 
WHERE email = 'user@example.com';

-- Count failed attempts
SELECT failed_login_attempts, COUNT(*) 
FROM user 
GROUP BY failed_login_attempts 
ORDER BY failed_login_attempts DESC;
```

---

## ⚙️ Configuration

### Adjust Rate Limits

Edit `backend/app/api/routes/login.py`:

```python
# Current: 5 attempts per 15 minutes
await rate_limiter.check_rate_limit(
    f"ip:{client_ip}",
    max_attempts=5,      # Change this
    window_minutes=15    # Change this
)
```

### Adjust Account Lockout

Edit `backend/app/utils/account_lockout.py`:

```python
# Current: Lock after 5 attempts for 1 hour
if user.failed_login_attempts >= 5:  # Change threshold
    user.locked_until = datetime.now() + timedelta(hours=1)  # Change duration
```

---

## 🐛 Troubleshooting

### "I'm locked out!"
```bash
docker-compose exec backend python manage_lockouts.py --unlock your@email.com
```

### "Rate limiting not working"
Check that Request object is passed to login endpoint and middleware is imported.

### "Lockout persists after timeout"
Expired locks auto-clear on next login attempt, or run:
```bash
docker-compose exec backend python manage_lockouts.py --unlock-expired
```

### "How do I see rate limiter state?"
Rate limiter is in-memory. Check logs or add this endpoint (dev only):
```python
@router.get("/debug/rate-limits")
def debug_rate_limits():
    return {
        "attempts": dict(rate_limiter.attempts),
        "blocked": dict(rate_limiter.blocked)
    }
```

---

## 📊 Monitoring

### What to Monitor

**Application Logs:**
```bash
# Watch for rate limit hits
docker-compose logs -f backend | grep "429"

# Watch for account lockouts
docker-compose logs -f backend | grep "423"
```

**Database Queries:**
```sql
-- Accounts with high failed attempts (potential attacks)
SELECT email, failed_login_attempts, locked_until
FROM user
WHERE failed_login_attempts > 2
ORDER BY failed_login_attempts DESC;
```

**Metrics to Track:**
- Number of 429 responses per hour (rate limit hits)
- Number of 423 responses per hour (lockouts)
- Average failed_login_attempts across all users
- Top IPs hitting rate limits

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Test rate limiting with real traffic patterns
- [ ] Configure monitoring for 429/423 responses
- [ ] Set up alerts for unusual lockout patterns
- [ ] Train support team on unlocking accounts
- [ ] Document unlock procedure for on-call
- [ ] Test admin utility script works in production
- [ ] Verify X-Forwarded-For header is set correctly
- [ ] Set up automated cleanup of old rate limit entries

---

## 📚 Related Documentation

- Full implementation: `RATE_LIMITING_IMPLEMENTATION.md`
- Summary: `BRUTE_FORCE_PROTECTION_SUMMARY.md`
- Security report: `SECURITY_VULNERABILITIES_REPORT.md` (HIGH-003)

---

## 💡 Tips

- **For E2E tests**: Create a test utility to bypass rate limiting
- **For load tests**: Increase thresholds temporarily or disable
- **For demos**: Be careful not to lock demo accounts
- **For staging**: Use production-like settings to catch issues early

---

**Questions?** Check the full documentation or ask the security team.

**Emergency unlock:** `docker-compose exec backend python manage_lockouts.py --unlock user@email.com`
