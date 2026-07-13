#!/usr/bin/env bash
# === FILE: scripts/deploy.sh ===
# Deployment script for Sinistri FNOL Agent
# Usage: ./scripts/deploy.sh [dev|staging|prod] [git-tag]

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────

REGION="eu-south-1"
CLUSTER="pratica-ai-cluster"
SERVICE="pratica-ai"
ECR_REPO="pratica-ai"

# ── Arguments ─────────────────────────────────────────────────

ENV="${1:-dev}"
TAG="${2:-$(git describe --tags --always 2>/dev/null || echo 'latest')}"

if [[ ! "$ENV" =~ ^(dev|staging|prod)$ ]]; then
    echo "❌ Usage: $0 [dev|staging|prod] [git-tag]"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo "  Sinistri FNOL Agent — Deployment"
echo "  Environment: $ENV"
echo "  Tag:         $TAG"
echo "  Region:      $REGION"
echo "═══════════════════════════════════════════════════════════"

# ── Step 1: Get AWS Account ID ────────────────────────────────

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"

echo ""
echo "▸ Step 1/7: Building Docker image..."
docker build -t "${ECR_REPO}:${TAG}" .
echo "✅ Docker image built: ${ECR_REPO}:${TAG}"

# ── Step 2: Run tests ─────────────────────────────────────────

echo ""
echo "▸ Step 2/7: Running tests..."
if [ -d "tests" ] && [ -n "$(ls -A tests/ 2>/dev/null)" ]; then
    python3 -m pytest tests/ -q --tb=short || {
        echo "❌ Tests failed. Aborting deployment."
        exit 1
    }
    echo "✅ Tests passed"
else
    echo "⚠️  No tests found in tests/ — skipping"
fi

# ── Step 3: Authenticate to ECR ───────────────────────────────

echo ""
echo "▸ Step 3/7: Authenticating to ECR..."
aws ecr get-login-password --region "$REGION" | \
    docker login --username AWS --password-stdin \
    "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
echo "✅ ECR authentication successful"

# ── Step 4: Tag image ─────────────────────────────────────────

echo ""
echo "▸ Step 4/7: Tagging image..."
docker tag "${ECR_REPO}:${TAG}" "${ECR_URI}:${TAG}"
docker tag "${ECR_REPO}:${TAG}" "${ECR_URI}:latest"
echo "✅ Tagged: ${ECR_URI}:${TAG}"

# ── Step 5: Push to ECR ───────────────────────────────────────

echo ""
echo "▸ Step 5/7: Pushing to ECR..."
docker push "${ECR_URI}:${TAG}"
docker push "${ECR_URI}:latest"
echo "✅ Image pushed to ECR"

# ── Step 6: Update ECS service ────────────────────────────────

echo ""
echo "▸ Step 6/7: Updating ECS service..."
aws ecs update-service \
    --cluster "$CLUSTER" \
    --service "$SERVICE" \
    --force-new-deployment \
    --region "$REGION" \
    --no-cli-pager

echo "⏳ Waiting for deployment to stabilize..."
aws ecs wait services-stable \
    --cluster "$CLUSTER" \
    --services "$SERVICE" \
    --region "$REGION"
echo "✅ ECS deployment stable"

# ── Step 7: Smoke test ────────────────────────────────────────

echo ""
echo "▸ Step 7/7: Running smoke test..."

# Get domain from tfvars
if [ -f "terraform/environments/${ENV}.tfvars" ]; then
    DOMAIN=$(grep 'domain_name' "terraform/environments/${ENV}.tfvars" | \
        sed 's/.*= *"\(.*\)"/\1/')
else
    # Fallback: get ALB DNS from Terraform output
    DOMAIN=$(cd terraform && terraform output -raw alb_dns_name 2>/dev/null || echo "")
fi

if [ -n "$DOMAIN" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://${DOMAIN}/health" --max-time 10 || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Smoke test passed (HTTP $HTTP_CODE)"
    else
        echo "⚠️  Smoke test returned HTTP $HTTP_CODE (expected 200)"
        echo "   URL: https://${DOMAIN}/health"
    fi
else
    echo "⚠️  Could not determine domain — skipping smoke test"
fi

# ── Done ──────────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Deployment complete!"
echo "  Environment: $ENV"
echo "  Image:       ${ECR_URI}:${TAG}"
echo "  Cluster:     $CLUSTER"
echo "═══════════════════════════════════════════════════════════"
