# Database Connection Encryption Setup

**Date:** October 12, 2025  
**Purpose:** Implement secure database connections with environment-aware SSL/TLS configuration

---

## Overview

This document explains how database connection encryption is configured in the AibenIQ application, addressing the security vulnerability identified in the security audit while maintaining compatibility with local Docker deployments.

## The Challenge

The security audit (LOW-004) identified that PostgreSQL connections lack encryption. However, a simple "always require SSL" approach doesn't work because:

1. **Local Docker Environment**: When PostgreSQL runs in the same Docker network as the application, SSL adds unnecessary overhead and complexity
2. **Production Environment**: When using external managed databases (AWS RDS, Azure PostgreSQL, etc.), SSL is essential for security
3. **Development Workflow**: Developers need friction-free local development without SSL certificate setup

## Solution: Environment-Aware SSL Configuration

The implementation automatically adjusts SSL settings based on:
- The `ENVIRONMENT` variable (`local`, `staging`, `production`)
- The database server hostname (detects Docker service names)
- An explicit `POSTGRES_SSL_MODE` configuration option

### SSL Modes Explained

| Mode | Description | When to Use |
|------|-------------|-------------|
| `disable` | No SSL encryption | Local Docker only (not recommended otherwise) |
| `allow` | Try non-SSL first, fall back to SSL | Transition scenarios |
| `prefer` | Try SSL first, fall back to non-SSL | **Default** - safe for all environments |
| `require` | Require SSL, don't verify certificate | External databases without cert verification |
| `verify-ca` | Require SSL and verify CA | Production with certificate authority |
| `verify-full` | Require SSL and verify hostname | **Most secure** - production recommended |

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# PostgreSQL SSL Mode Configuration
POSTGRES_SSL_MODE=prefer  # Default: safe for all environments
```

### Environment-Specific Recommendations

#### Local Development (Docker)
```bash
ENVIRONMENT=local
POSTGRES_SERVER=db  # Docker service name
POSTGRES_SSL_MODE=prefer  # Auto-disables for Docker db service
```

**Result**: SSL is automatically disabled for `db` service to avoid overhead.

#### Staging/Production (Docker on same EC2)
```bash
ENVIRONMENT=production
POSTGRES_SERVER=db  # Still in same Docker network
POSTGRES_SSL_MODE=disable  # Explicitly disable for same-instance Docker
```

**Note**: When Postgres is in the same Docker Compose stack on the same EC2 instance, the connection never leaves the machine, so encryption is optional. Set to `disable` for performance.

#### Production (External Managed Database)
```bash
ENVIRONMENT=production
POSTGRES_SERVER=mydb.abc123.us-east-1.rds.amazonaws.com
POSTGRES_SSL_MODE=require  # or verify-full with certificates
```

**Result**: SSL is required for connections to external database servers.

## Auto-Detection Logic

The application automatically detects local Docker environments:

```python
# Auto-detect local Docker environment
is_local_docker = self.POSTGRES_SERVER in ["db", "localhost", "127.0.0.1"]

# If in local environment and using Docker db service, disable SSL
if self.ENVIRONMENT == "local" and is_local_docker and ssl_mode == "prefer":
    ssl_mode = "disable"
```

This means:
- ✅ `ENVIRONMENT=local` + `POSTGRES_SERVER=db` → SSL disabled automatically
- ✅ `ENVIRONMENT=production` + `POSTGRES_SERVER=rds.amazonaws.com` → SSL enabled
- ✅ `POSTGRES_SSL_MODE=require` → Always enforces SSL regardless of environment

## Advanced: Certificate Verification

For maximum security in production, use certificate verification:

### Step 1: Obtain SSL Certificates

**AWS RDS:**
```bash
# Download RDS certificate bundle
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -O /app/certs/rds-ca-bundle.pem
```

**Azure PostgreSQL:**
```bash
# Download Azure certificate
wget https://dl.cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem -O /app/certs/azure-ca.pem
```

### Step 2: Update Configuration

```bash
POSTGRES_SSL_MODE=verify-full
POSTGRES_SSLROOTCERT=/app/certs/rds-ca-bundle.pem
```

### Step 3: Mount Certificates in Docker

Update `docker-compose.yml`:

```yaml
backend:
  volumes:
    - ./certs:/app/certs:ro  # Mount certificates as read-only
```

### Step 4: Extend Config (Advanced)

For full certificate support, extend `config.py`:

```python
POSTGRES_SSLROOTCERT: str = ""  # Path to CA certificate
POSTGRES_SSLCERT: str = ""      # Path to client certificate
POSTGRES_SSLKEY: str = ""       # Path to client key

@computed_field
@property
def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
    # Build query parameters
    query_parts = []
    
    if ssl_mode and ssl_mode != "disable":
        query_parts.append(f"sslmode={ssl_mode}")
        
        if self.POSTGRES_SSLROOTCERT:
            query_parts.append(f"sslrootcert={self.POSTGRES_SSLROOTCERT}")
        
        if self.POSTGRES_SSLCERT:
            query_parts.append(f"sslcert={self.POSTGRES_SSLCERT}")
        
        if self.POSTGRES_SSLKEY:
            query_parts.append(f"sslkey={self.POSTGRES_SSLKEY}")
    
    query_params = "&".join(query_parts) if query_parts else None
    
    return MultiHostUrl.build(
        scheme="postgresql+psycopg",
        username=self.POSTGRES_USER,
        password=self.POSTGRES_PASSWORD,
        host=self.POSTGRES_SERVER,
        port=self.POSTGRES_PORT,
        path=self.POSTGRES_DB,
        query=query_params,
    )
```

## Testing SSL Connections

### Verify SSL is Active

Connect to your database and check SSL status:

```bash
# Enter backend container
docker exec -it <backend-container> bash

# Connect to database
psql $SQLALCHEMY_DATABASE_URI

# Check SSL status
SELECT ssl, version FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

Expected output for SSL-enabled connection:
```
 ssl |        version        
-----+----------------------
 t   | TLSv1.3
```

### Test Connection Modes

```bash
# Test with SSL required
POSTGRES_SSL_MODE=require python -c "from app.core.db import engine; engine.connect()"

# Test with SSL disabled
POSTGRES_SSL_MODE=disable python -c "from app.core.db import engine; engine.connect()"
```

## Common Scenarios

### Scenario 1: Local Development
**Setup:** Docker Compose on laptop  
**Configuration:**
```bash
ENVIRONMENT=local
POSTGRES_SERVER=db
POSTGRES_SSL_MODE=prefer  # or omit, uses default
```
**Result:** SSL automatically disabled for performance ✅

### Scenario 2: Production on Same EC2 Instance
**Setup:** Docker Compose with Postgres on same EC2  
**Configuration:**
```bash
ENVIRONMENT=production
POSTGRES_SERVER=db
POSTGRES_SSL_MODE=disable  # Explicitly disable
```
**Result:** No SSL overhead for same-instance connections ✅

### Scenario 3: Production with AWS RDS
**Setup:** Application on EC2, Database on RDS  
**Configuration:**
```bash
ENVIRONMENT=production
POSTGRES_SERVER=myapp.abc123.us-east-1.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_SSL_MODE=require  # or verify-full
```
**Result:** All connections encrypted with TLS ✅

### Scenario 4: Staging with Azure PostgreSQL
**Setup:** Application on Azure VM, Database on Azure PostgreSQL  
**Configuration:**
```bash
ENVIRONMENT=staging
POSTGRES_SERVER=myapp.postgres.database.azure.com
POSTGRES_PORT=5432
POSTGRES_SSL_MODE=require
```
**Result:** SSL required by Azure enforced ✅

## Security Best Practices

### ✅ DO

- Use `POSTGRES_SSL_MODE=require` or higher for external databases
- Use `verify-full` in production with proper certificates
- Keep certificates in a secure, read-only volume
- Rotate certificates before expiration
- Monitor SSL connection metrics

### ❌ DON'T

- Use `disable` for external/cloud databases
- Use `allow` in production (too permissive)
- Commit SSL certificates to version control
- Use self-signed certificates in production
- Ignore certificate expiration warnings

## Troubleshooting

### Error: "SSL connection has been closed unexpectedly"

**Cause:** Database requires SSL but connection is non-SSL  
**Solution:** Set `POSTGRES_SSL_MODE=require`

### Error: "root certificate file does not exist"

**Cause:** `verify-ca` or `verify-full` mode without certificate  
**Solution:** Provide certificate path or use `require` mode

### Error: "certificate verify failed"

**Cause:** Hostname mismatch or expired certificate  
**Solution:** 
- Verify hostname matches certificate CN/SAN
- Check certificate expiration date
- Use `require` instead of `verify-full` if CN doesn't match

### Performance Impact

**Question:** Does SSL slow down database connections?

**Answer:** 
- Initial handshake: ~10-50ms overhead
- Ongoing queries: ~1-5% performance impact
- Connection pooling mitigates handshake cost
- For same-instance Docker: unnecessary overhead
- For external databases: security benefit outweighs cost

## Migration Guide

### Existing Deployments

To enable SSL on existing deployments:

1. **Check current environment:**
   ```bash
   echo $POSTGRES_SERVER
   echo $ENVIRONMENT
   ```

2. **Update `.env` file:**
   ```bash
   # Add SSL mode configuration
   POSTGRES_SSL_MODE=require  # For external databases
   # or
   POSTGRES_SSL_MODE=disable  # For same-instance Docker
   ```

3. **Restart services:**
   ```bash
   docker-compose restart backend prestart
   ```

4. **Verify connection:**
   ```bash
   docker-compose logs backend | grep -i ssl
   ```

### New Deployments

For new deployments, the `.env.example` includes `POSTGRES_SSL_MODE=prefer` by default, which is safe for all environments.

## Compliance & Auditing

This implementation addresses:

- ✅ **Security Audit LOW-004**: Database connection encryption
- ✅ **GDPR/HIPAA**: Encryption of data in transit
- ✅ **SOC 2**: Secure database connections
- ✅ **PCI DSS**: Encrypted transmission of cardholder data

## References

- [PostgreSQL SSL Documentation](https://www.postgresql.org/docs/current/libpq-ssl.html)
- [psycopg SSL Parameters](https://www.psycopg.org/psycopg3/docs/basic/params.html)
- [AWS RDS SSL/TLS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html)
- [Azure PostgreSQL SSL](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-connect-tls-ssl)

---

**Last Updated:** October 12, 2025  
**Maintained By:** Security & Infrastructure Team
