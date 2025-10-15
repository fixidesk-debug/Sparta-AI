#!/usr/bin/env bash
# Deploy images to staging Kubernetes cluster (EKS/GKE/AKS)
# Assumes KUBECONFIG is configured via CI (OIDC or kubectl setup)
set -euo pipefail

NAMESPACE=${NAMESPACE:-sparta-staging}
DEPLOYMENT=sparta-backend
IMAGE=${IMAGE:-${DOCKERHUB_USERNAME}/sparta-backend:${GITHUB_SHA}}

kubectl -n $NAMESPACE set image deployment/$DEPLOYMENT $DEPLOYMENT=$IMAGE --record
kubectl -n $NAMESPACE rollout status deployment/$DEPLOYMENT

echo "Staging deployment updated to $IMAGE"
