# === FILE: terraform/secrets.tf ===
# AWS Secrets Manager for Sinistri FNOL Agent
# Sensitive credentials stored securely, never in tfstate plaintext

# ── Google API Key ────────────────────────────────────────────

resource "aws_secretsmanager_secret" "google_api_key" {
  name                    = "${var.app_name}/google-api-key"
  description             = "Google Gemini API key for the FNOL voice agent"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.app_name}-google-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "google_api_key" {
  secret_id     = aws_secretsmanager_secret.google_api_key.id
  secret_string = var.google_api_key
}

# ── Application Secret Key (JWT signing) ──────────────────────

resource "aws_secretsmanager_secret" "secret_key" {
  name                    = "${var.app_name}/secret-key"
  description             = "JWT signing key for operator authentication"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.app_name}-secret-key"
  }
}

resource "aws_secretsmanager_secret_version" "secret_key" {
  secret_id     = aws_secretsmanager_secret.secret_key.id
  secret_string = var.secret_key
}

# ── Database Credentials ──────────────────────────────────────

resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.app_name}/db-credentials"
  description             = "PostgreSQL credentials for pratica_ai_db database"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.app_name}-db-credentials"
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = random_password.db_password.result
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    dbname   = aws_db_instance.main.db_name
  })
}

# ── Redis Auth Token ──────────────────────────────────────────

resource "aws_secretsmanager_secret" "redis_auth_token" {
  name                    = "${var.app_name}/redis-auth-token"
  description             = "ElastiCache Redis authentication token"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.app_name}-redis-auth-token"
  }
}

resource "aws_secretsmanager_secret_version" "redis_auth_token" {
  secret_id     = aws_secretsmanager_secret.redis_auth_token.id
  secret_string = random_password.redis_auth_token.result
}

# ── IAM Policy: Allow ECS to read secrets ─────────────────────

resource "aws_iam_policy" "secrets_read" {
  name        = "${var.app_name}-secrets-read"
  description = "Allow ECS tasks to read Secrets Manager secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue"
      ]
      Resource = [
        aws_secretsmanager_secret.google_api_key.arn,
        aws_secretsmanager_secret.secret_key.arn,
        aws_secretsmanager_secret.db_credentials.arn,
        aws_secretsmanager_secret.redis_auth_token.arn,
      ]
    }]
  })
}
