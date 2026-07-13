# === FILE: terraform/security_groups.tf ===
# Security groups for Sinistri FNOL Agent
# GDPR data flow: Internet → ALB → App → DB/Redis (private)

# ── 1. ALB Security Group ─────────────────────────────────────
# Allows inbound HTTP/HTTPS from the internet

resource "aws_security_group" "alb" {
  name        = "${var.app_name}-alb-sg"
  description = "ALB - allows HTTP/HTTPS from internet (GDPR: entry point)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-alb-sg"
  }
}

# ── 2. Application Security Group ─────────────────────────────
# Allows inbound from ALB on port 4177 only

resource "aws_security_group" "app" {
  name        = "${var.app_name}-app-sg"
  description = "App - allows 4177 from ALB only (GDPR: application tier)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "App port from ALB"
    from_port       = 4177
    to_port         = 4177
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "All outbound (Gemini API, DB, Redis)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-app-sg"
  }
}

# ── 3. Database Security Group ────────────────────────────────
# Allows inbound from App on port 5432 only (PostgreSQL)

resource "aws_security_group" "db" {
  name        = "${var.app_name}-db-sg"
  description = "RDS - allows 5432 from App only (GDPR: data at rest)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from App"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-db-sg"
  }
}

# ── 4. Redis Security Group ───────────────────────────────────
# Allows inbound from App on port 6379 only

resource "aws_security_group" "redis" {
  name        = "${var.app_name}-redis-sg"
  description = "Redis - allows 6379 from App only (GDPR: session cache)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Redis from App"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-redis-sg"
  }
}
