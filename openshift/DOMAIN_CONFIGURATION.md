# Centralized Domain Configuration

This implementation provides a centralized approach to managing domain configurations across different environments, making it easier to maintain and switch between branches during development.

## Architecture

### Base Configuration

- **`openshift/base/domain-config.yaml`**: Contains the base domain configuration with all service URLs
- **Base manifests**: Use RedHat production domains by default

### Environment-Specific Overrides

- **`openshift/overlays/development/`**: Development-specific domain patches with `-dev` suffix
- **`openshift/overlays/production/`**: Production-specific domain patches (RedHat URLs)

## Service URLs

### Production Environment (RedHat)

- **Frontend**: `redhat.aiben.io`
- **Backend API**: `redhat-api.aiben.io`
- **Traefik Dashboard**: `redhat-traefik.aiben.io`
- **Adminer**: `redhat-adminer.aiben.io`

### Development Environment

- **Frontend**: `redhat-dev.aiben.io`
- **Backend API**: `redhat-api-dev.aiben.io`
- **Traefik Dashboard**: `redhat-traefik-dev.aiben.io`
- **Adminer**: `redhat-adminer-dev.aiben.io`

## How It Works

1. **Base Configuration**: Defines production-ready RedHat domains
2. **Environment Patches**: Override specific domains per environment using `patchesStrategicMerge`
3. **Service Manifests**: All services (frontend, backend, traefik, adminer) included with proper routing
4. **Automatic Switching**: When you switch Git branches, the correct environment configuration is applied

## Files Structure

### Base Files

- `openshift/base/domain-config.yaml` - Centralized domain configuration with all service URLs
- `openshift/base/frontend.yaml` - Frontend deployment with RedHat route
- `openshift/base/backend.yaml` - Backend deployment with RedHat API route
- `openshift/base/traefik.yaml` - Traefik deployment with dashboard route
- `openshift/base/adminer.yaml` - Adminer deployment for database management
- `openshift/base/kustomization.yaml` - Includes all services

### Environment Overlays

- `openshift/overlays/development/domain-config-patch.yaml` - Dev URLs with `-dev` suffix
- `openshift/overlays/development/route-patches.yaml` - Development route overrides
- `openshift/overlays/development/configmap-patch.yaml` - Development API URLs
- `openshift/overlays/production/domain-config-patch.yaml` - Production RedHat URLs
- `openshift/overlays/production/route-patches.yaml` - Production route overrides
- `openshift/overlays/production/configmap-patch.yaml` - Production API URLs

## Benefits

✅ **All Services Defined**: Frontend, Backend, Traefik, Adminer all configured
✅ **Single Source of Truth**: All service URLs defined in domain-config per environment
✅ **Branch Awareness**: Automatically switches domains when changing Git branches
✅ **Environment Isolation**: Clear separation between dev and prod domains
✅ **Easy Maintenance**: Change URLs in one place per environment
✅ **No Manual Substitution**: No need for environment variables or manual find/replace
✅ **Production Ready**: Uses your specific RedHat URLs

## Usage

### To Change Service URLs

Edit the appropriate `domain-config-patch.yaml`:

**For Production:**

```yaml
# openshift/overlays/production/domain-config-patch.yaml
data:
  FRONTEND_URL: "redhat.aiben.io"
  API_URL: "redhat-api.aiben.io"
  TRAEFIK_URL: "redhat-traefik.aiben.io"
  ADMINER_URL: "redhat-adminer.aiben.io"
```

**For Development:**

```yaml
# openshift/overlays/development/domain-config-patch.yaml
data:
  FRONTEND_URL: "redhat-dev.aiben.io"
  API_URL: "redhat-api-dev.aiben.io"
  TRAEFIK_URL: "redhat-traefik-dev.aiben.io"
  ADMINER_URL: "redhat-adminer-dev.aiben.io"
```

### Testing

```bash
# Test production configuration with your RedHat URLs
kustomize build openshift/overlays/production

# Test development configuration with dev URLs
kustomize build openshift/overlays/development
```

### Adding New Services

1. Create the service manifest in `openshift/base/`
2. Add the service URL to `domain-config.yaml`
3. Add route patches in both development and production overlays
4. Update the base `kustomization.yaml`

This approach ensures that when you switch branches during development, the correct domain configuration is automatically applied without needing to manually manage environment variables or configuration files.

- **`openshift/base/domain-config.yaml`**: Contains the base domain configuration
- **Base manifests**: Use default `yourdomain.com` domains that work for production

### Environment-Specific Overrides

- **`openshift/overlays/development/`**: Development-specific domain patches
- **`openshift/overlays/production/`**: Production-specific domain patches

## Domain Structure

### Development Environment

- **API**: `api-dev.yourdomain.com`
- **Dashboard**: `dashboard-dev.yourdomain.com`
- **CORS Origins**: Includes localhost + development dashboard

### Production Environment

- **API**: `api.yourdomain.com`
- **Dashboard**: `dashboard.yourdomain.com`
- **CORS Origins**: Production dashboard only

## How It Works

1. **Base Configuration**: Defines default production-ready domains
2. **Environment Patches**: Override specific domains per environment using `patchesStrategicMerge`
3. **Automatic Switching**: When you switch Git branches, the correct environment configuration is applied

## Files Modified

### Base Files

- `openshift/base/domain-config.yaml` - Centralized domain configuration
- `openshift/base/kustomization.yaml` - Added domain-config resource

### Development Overlay

- `openshift/overlays/development/domain-config-patch.yaml` - Dev domain config
- `openshift/overlays/development/route-patches.yaml` - Dev route overrides
- `openshift/overlays/development/configmap-patch.yaml` - Dev API URLs
- `openshift/overlays/development/kustomization.yaml` - Added route patches

### Production Overlay

- `openshift/overlays/production/domain-config-patch.yaml` - Prod domain config
- `openshift/overlays/production/route-patches.yaml` - Prod route overrides
- `openshift/overlays/production/configmap-patch.yaml` - Prod API URLs
- `openshift/overlays/production/kustomization.yaml` - Added route patches

## Benefits

✅ **Single Source of Truth**: Domain only needs to be changed in one place per environment
✅ **Branch Awareness**: Automatically switches domains when changing Git branches
✅ **Environment Isolation**: Clear separation between dev and prod domains
✅ **Easy Maintenance**: No need to update multiple files when domains change
✅ **No Manual Substitution**: No need for environment variables or manual find/replace

## Usage

### To Change the Base Domain

Edit `openshift/base/domain-config.yaml`:

```yaml
data:
  BASE_DOMAIN: "yournewdomain.com"
```

### To Add a New Environment

1. Create `openshift/overlays/staging/` directory
2. Copy and modify files from development overlay
3. Update domain-config-patch.yaml with staging-specific values

### Testing

```bash
# Test development configuration
kustomize build openshift/overlays/development

# Test production configuration
kustomize build openshift/overlays/production
```

This approach ensures that when you switch branches during development, the correct domain configuration is automatically applied without needing to manually manage environment variables or configuration files.
