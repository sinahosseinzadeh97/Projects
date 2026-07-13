#!/usr/bin/env bash
# === FILE: scripts/terraform-init.sh ===
# One-time Terraform initialization for Sinistri FNOL Agent
# Creates S3 state bucket + DynamoDB lock table, then runs terraform init

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────

REGION="eu-south-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
STATE_BUCKET="sinistri-terraform-state-${ACCOUNT_ID}"
LOCK_TABLE="sinistri-terraform-lock"

echo "═══════════════════════════════════════════════════════════"
echo "  Sinistri FNOL Agent — Terraform Initialization"
echo "  Region:  $REGION"
echo "  Account: $ACCOUNT_ID"
echo "  Bucket:  $STATE_BUCKET"
echo "═══════════════════════════════════════════════════════════"

# ── Step 1: Create S3 bucket for Terraform state ──────────────

echo ""
echo "▸ Step 1/4: Creating S3 state bucket..."

if aws s3api head-bucket --bucket "$STATE_BUCKET" 2>/dev/null; then
    echo "  Bucket already exists: $STATE_BUCKET"
else
    aws s3api create-bucket \
        --bucket "$STATE_BUCKET" \
        --region "$REGION" \
        --create-bucket-configuration LocationConstraint="$REGION"

    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "$STATE_BUCKET" \
        --versioning-configuration Status=Enabled

    # Enable encryption
    aws s3api put-bucket-encryption \
        --bucket "$STATE_BUCKET" \
        --server-side-encryption-configuration '{
            "Rules": [{
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "aws:kms"
                },
                "BucketKeyEnabled": true
            }]
        }'

    # Block public access
    aws s3api put-public-access-block \
        --bucket "$STATE_BUCKET" \
        --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

    echo "✅ S3 bucket created with versioning + encryption"
fi

# ── Step 2: Create DynamoDB table for state locking ───────────

echo ""
echo "▸ Step 2/4: Creating DynamoDB lock table..."

if aws dynamodb describe-table --table-name "$LOCK_TABLE" --region "$REGION" >/dev/null 2>&1; then
    echo "  Lock table already exists: $LOCK_TABLE"
else
    aws dynamodb create-table \
        --table-name "$LOCK_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "$REGION"

    aws dynamodb wait table-exists \
        --table-name "$LOCK_TABLE" \
        --region "$REGION"

    echo "✅ DynamoDB lock table created"
fi

# ── Step 3: Run terraform init ────────────────────────────────

echo ""
echo "▸ Step 3/4: Running terraform init..."

cd terraform

# Update backend config with actual bucket name
terraform init \
    -backend-config="bucket=${STATE_BUCKET}" \
    -backend-config="region=${REGION}" \
    -backend-config="dynamodb_table=${LOCK_TABLE}" \
    -backend-config="encrypt=true"

echo "✅ Terraform initialized"

# ── Step 4: Run terraform plan ────────────────────────────────

echo ""
echo "▸ Step 4/4: Running terraform plan (dev)..."

terraform plan \
    -var-file=environments/dev.tfvars \
    -var="google_api_key=PLACEHOLDER_REPLACE_ME" \
    -var="secret_key=PLACEHOLDER_REPLACE_ME" \
    -out=plan.tfplan

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Terraform initialization complete!"
echo ""
echo "  State bucket:  $STATE_BUCKET"
echo "  Lock table:    $LOCK_TABLE"
echo ""
echo "  To apply the plan:"
echo "    cd terraform && terraform apply plan.tfplan"
echo ""
echo "  To plan for production:"
echo "    terraform plan -var-file=environments/prod.tfvars"
echo "═══════════════════════════════════════════════════════════"
