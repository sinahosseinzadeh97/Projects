# === FILE: terraform/rds.tf ===
# AWS RDS PostgreSQL for Sinistri FNOL Agent
# Encrypted at rest, GDPR-compliant backup retention

# ── DB Subnet Group ───────────────────────────────────────────

resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.app_name}-db-subnet-group"
  }
}

# ── DB Parameter Group (audit logging for GDPR) ──────────────

resource "aws_db_parameter_group" "main" {
  family = "postgres16"
  name   = "${var.app_name}-pg16-params"

  # GDPR audit logging — log data-modifying statements
  parameter {
    name  = "log_statement"
    value = "mod"
  }

  # Log slow queries (>1s) for performance monitoring
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  # Enable query logging for compliance audit
  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  tags = {
    Name = "${var.app_name}-pg16-params"
  }
}

# ── RDS Instance ──────────────────────────────────────────────

resource "aws_db_instance" "main" {
  identifier = "${var.app_name}-db"

  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class

  db_name  = "pratica_ai_db"
  username = "sinistri_user"
  password = random_password.db_password.result

  # Storage — encrypted for insurance data
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true # Mandatory for insurance personal data

  # Multi-AZ: false for dev, true for prod
  multi_az = var.environment == "prod" ? true : false

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false

  # Parameter group with audit logging
  parameter_group_name = aws_db_parameter_group.main.name

  # Backup — 30 days retention for GDPR/IVASS compliance
  backup_retention_period = 30
  backup_window           = "02:00-03:00"       # Italian night (UTC+2 = 04:00-05:00 local)
  maintenance_window      = "Mon:03:00-Mon:04:00"

  # Performance Insights
  performance_insights_enabled          = true
  performance_insights_retention_period = 7

  # Deletion protection — enabled for prod
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${var.app_name}-final-snapshot" : null

  # Enable CloudWatch logs export
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Name      = "${var.app_name}-db"
    GDPRData  = "true"
    Encrypted = "true"
  }
}

# ── Random password for RDS ───────────────────────────────────

resource "random_password" "db_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}:?"
}
