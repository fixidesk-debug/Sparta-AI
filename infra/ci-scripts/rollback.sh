#!/usr/bin/env bash
# Rollback helper: roll back a deployment to previous revision
set -euo pipefail

DEPLOYMENT=${1:?deployment}
NAMESPACE=${2:-sparta}

kubectl -n $NAMESPACE rollout undo deployment/$DEPLOYMENT
kubectl -n $NAMESPACE rollout status deployment/$DEPLOYMENT

echo "Rolled back $DEPLOYMENT in namespace $NAMESPACE"
