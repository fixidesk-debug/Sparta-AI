#!/usr/bin/env bash
# Blue-green deployment helper for Kubernetes
# Usage: blue_green_deploy.sh <service> <image> <namespace>
set -euo pipefail

SERVICE=${1:?service}
IMAGE=${2:?image}
NAMESPACE=${3:-sparta}

# Determine active color by checking service selector
ACTIVE_COLOR=$(kubectl -n $NAMESPACE get svc $SERVICE -o jsonpath='{.spec.selector.color}' || echo "blue")
if [ "$ACTIVE_COLOR" = "blue" ]; then
  NEW_COLOR=green
else
  NEW_COLOR=blue
fi

# Create new deployment name
NEW_DEPLOYMENT=${SERVICE}-${NEW_COLOR}

# Patch deployment template (assumes a template exists as ${SERVICE}-template)
kubectl -n $NAMESPACE set image deployment/${SERVICE}-${NEW_COLOR} ${SERVICE}=${IMAGE} --record || \
  kubectl -n $NAMESPACE create deployment $NEW_DEPLOYMENT --image=${IMAGE}

kubectl -n $NAMESPACE rollout status deployment/${NEW_DEPLOYMENT}

# Switch service selector to new color
kubectl -n $NAMESPACE patch svc $SERVICE -p "{\"spec\":{\"selector\":{\"color\":\"${NEW_COLOR}\"}}}"

# Wait and verify
sleep 5
kubectl -n $NAMESPACE get pods -l color=${NEW_COLOR}

echo "Blue-green deploy complete. Service $SERVICE now points to $NEW_COLOR"
