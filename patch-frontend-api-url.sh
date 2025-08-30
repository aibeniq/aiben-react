#!/bin/bash

# Script to patch the frontend API URL in the running container
# This is a temporary workaround until the build process is fixed

echo "Patching frontend API URL to use correct backend..."

# Get the current frontend pod
FRONTEND_POD=$(oc get pod -l component=frontend -o jsonpath='{.items[0].metadata.name}')
echo "Frontend pod: $FRONTEND_POD"

# Create a new pod that can modify the frontend assets
oc run temp-patcher --image=busybox --rm -i --restart=Never -- sh -c "
# Copy the current frontend assets
mkdir -p /tmp/frontend
oc cp $FRONTEND_POD:/usr/share/nginx/html /tmp/frontend/

# Replace the hardcoded API URL
find /tmp/frontend/html -name '*.js' -exec sed -i 's|https://api-aibeniq-prod.apps.your-cluster.com|https://redhat-api.aiben.io|g' {} \;

# Copy back the patched assets
oc cp /tmp/frontend/html $FRONTEND_POD:/usr/share/nginx/
"

echo "Frontend patched! Please refresh your browser."
