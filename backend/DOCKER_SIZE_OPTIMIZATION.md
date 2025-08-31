# Docker Image Size Optimization

## Problem Solved

The original Docker image was **11.3GB** due to PyTorch+CUDA libraries being installed during the build process. This caused:

- Push timeouts to OpenShift registry
- Deployment failures
- Excessive resource usage
- Long build times

## Solution: Lazy Loading Architecture

We've implemented a **lazy loading system** that allows the application to run without PyTorch dependencies installed, loading them only when needed. This reduces the base image size from **11.3GB to ~500MB-1GB**.

## Architecture Overview

### Core Components

1. **`app/core/ml_imports.py`** - Lazy loading module

   - Conditionally imports ML libraries only when needed
   - Provides graceful fallbacks when dependencies are unavailable
   - Supports runtime installation based on environment variables

2. **Lean Dependencies** - `pyproject.lean.toml`

   - Removes PyTorch-dependent packages from base installation
   - Keeps OpenAI, AWS Bedrock, and Ollama support
   - ML packages become optional dependencies

3. **Environment-Based Configuration**
   - `ENABLE_PYTORCH=false` - Disables PyTorch features
   - `RUNTIME_INSTALL_PYTORCH=true` - Enables on-demand installation

## Deployment Options

### Option 1: Lean Deployment (Recommended)

```dockerfile
# Use: Dockerfile.lean
# Size: ~500MB-1GB
# Features: OpenAI, AWS Bedrock, Ollama
```

**Pros:**

- Fastest deployments
- Lowest resource usage
- Best for OpenAI-only deployments
- Immediate startup

**Cons:**

- HuggingFace models not available by default

### Option 2: Runtime Installation

```dockerfile
# Use: Dockerfile.lean + environment variables
# Size: ~500MB-1GB (base) + runtime ML installation
# Features: All providers (ML installed on first use)
```

**Environment Variables:**

```bash
RUNTIME_INSTALL_PYTORCH=true
ENABLE_PYTORCH=true
```

**Pros:**

- Small base image
- Full ML capabilities available on demand
- One-time installation cost

**Cons:**

- First ML operation has installation delay
- Requires internet access for package installation

### Option 3: Full Deployment

```dockerfile
# Use: Dockerfile (original)
# Size: Larger (~2-3GB, optimized from 11.3GB)
# Features: All ML capabilities pre-installed
```

**Pros:**

- All features immediately available
- No runtime installation delays

**Cons:**

- Larger image size
- Longer deployment times

## Technical Implementation

### Lazy Loading Pattern

```python
# Before (direct import - causes large image)
from sentence_transformers import SentenceTransformer

# After (lazy loading)
from app.core.ml_imports import get_sentence_transformers

SentenceTransformer = get_sentence_transformers()
if SentenceTransformer is None:
    # Graceful fallback - suggest OpenAI/AWS/Ollama
    raise HTTPException(...)
```

### Model Initialization Updates

**Before:**

```python
def initialize_default_models():
    default_models = [
        {"provider": "HUGGINGFACE", ...},  # Always included
        {"provider": "OPENAI", ...},
        # ...
    ]
```

**After:**

```python
def initialize_default_models():
    default_models = [
        {"provider": "OPENAI", ...},  # Prioritized
        {"provider": "AWS", ...},
    ]

    # Only add HuggingFace if ML capabilities available
    if check_ml_capabilities():
        default_models.extend([
            {"provider": "HUGGINGFACE", ...}
        ])
```

## Build and Deployment

### Building Images

```powershell
# Build lean version only
.\build-optimized.ps1 -LeanOnly

# Build both versions
.\build-optimized.ps1

# Build and push to registry
.\build-optimized.ps1 -Push -Version "v1.1.0"
```

### OpenShift Deployment

```yaml
# Lean deployment (recommended)
spec:
  containers:
    - name: backend
      image: image-registry.openshift-image-registry.svc:5000/aibeniq-dev/aibeniq-backend-lean:v1.0.0
      env:
        - name: ENABLE_PYTORCH
          value: "false"
```

```yaml
# Runtime ML installation
spec:
  containers:
    - name: backend
      image: image-registry.openshift-image-registry.svc:5000/aibeniq-dev/aibeniq-backend-lean:v1.0.0
      env:
        - name: RUNTIME_INSTALL_PYTORCH
          value: "true"
        - name: ENABLE_PYTORCH
          value: "true"
```

## Size Comparison

| Version        | Size                 | Features               | Use Case                 |
| -------------- | -------------------- | ---------------------- | ------------------------ |
| Original       | 11.3GB               | All ML                 | Development only         |
| Lean           | ~500MB-1GB           | OpenAI/AWS/Ollama      | Production (recommended) |
| Runtime ML     | ~500MB-1GB + runtime | All (on-demand)        | Hybrid approach          |
| Full Optimized | ~2-3GB               | All ML (pre-installed) | Heavy ML workloads       |

## Migration Path

1. **Immediate**: Deploy lean version for OpenAI-only usage
2. **Gradual**: Test runtime ML installation in staging
3. **Full**: Move to full optimized version if needed

## Performance Impact

- **Startup time**: Lean version starts immediately
- **First ML operation**: Runtime installation adds ~30-60 seconds one-time delay
- **Subsequent operations**: No performance difference
- **Memory usage**: Significantly reduced base footprint

## Monitoring and Debugging

### Check ML Capabilities

```python
from app.core.ml_imports import check_ml_capabilities
ml_available = check_ml_capabilities()
```

### Environment Status

```bash
# Check if PyTorch would be installed at runtime
echo $RUNTIME_INSTALL_PYTORCH

# Check current ML status
curl http://localhost:8000/api/v1/embedding-models/
```

### Logs to Monitor

- ML capability checks on startup
- Runtime installation progress
- Graceful fallbacks to OpenAI/AWS providers

## Security Considerations

- Runtime installation requires internet access
- Package integrity verified through pip/uv
- No additional attack surface in lean deployments
- ML packages isolated to runtime environment

## Future Enhancements

1. **Pre-built ML Extensions**: Optional sidecar containers with ML capabilities
2. **Progressive Loading**: Download models on-demand rather than all dependencies
3. **Caching Layer**: Shared ML package cache across deployments
4. **Health Checks**: Monitor ML capability status

## Troubleshooting

### Issue: ML features not working in lean deployment

**Solution**: Set `RUNTIME_INSTALL_PYTORCH=true` or use full image

### Issue: Runtime installation fails

**Solution**:

- Check internet connectivity
- Verify container has write permissions
- Use full pre-built image instead

### Issue: Large image still being built

**Solution**: Ensure using `Dockerfile.lean` and `pyproject.lean.toml`

### Issue: HuggingFace models showing as unavailable

**Expected behavior** in lean deployment - configure runtime installation or use OpenAI/AWS alternatives
