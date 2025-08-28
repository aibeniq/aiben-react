# Service Selector Mismatch Fix - August 27, 2025

## Problem

Backend pods were stuck in `Init:0/1` status because the postgres service selector didn't match the postgres pod labels.

## Root Cause

- **Production service** had selector: `app: aibeniq, component: database, environment: production, version: v1`
- **Kustomize deployment** only generated labels: `app: aibeniq, component: database`
- This caused service to have no endpoints, preventing backend init containers from connecting

## Immediate Fix Applied

Updated production service selector to match deployment labels:

```bash
oc apply -f postgres-service-fixed.yaml -n aibeniq-prod
```

## Permanent Fix Implemented

1. **Updated `openshift/base/kustomization.yaml`**: Added `environment: production` to `commonLabels`
2. **Updated `openshift/base/postgres.yaml`**: Added complete label set to service selector

## Prevention Strategy

- **All resource definitions now use Kustomize** for consistent labeling
- **Service selectors match deployment labels exactly**
- **CommonLabels in Kustomization ensure consistency across all resources**

## Verification

```bash
# Check service has endpoints
oc get endpoints postgres -n aibeniq-prod

# Check backend pods can connect
oc logs backend-<pod-name> -c wait-for-postgres -n aibeniq-prod
```

## Result

✅ Backend init containers now successfully connect to postgres
✅ Service selector mismatch will not occur in future deployments
✅ Pause/resume cycles will maintain proper label consistency
